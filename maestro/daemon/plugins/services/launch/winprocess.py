import win32api, win32process, win32security
import win32event, win32con, msvcrt, win32gui
import pywintypes
import win32pipe, win32file, os

#import os
#import sys
#import threading
#import types
#import pprint 
#import errno
import logging
#import msvcrt
#import win32api
#import win32file
#import win32pipe
#import pywintypes
#import win32process
#import win32event
#import win32security
#import win32con
# constants pulled from win32con to save memory
VER_PLATFORM_WIN32_WINDOWS = 1
CTRL_BREAK_EVENT = 1
SW_SHOWDEFAULT = 10
WM_CLOSE = 0x10
DUPLICATE_SAME_ACCESS = 2

# Loggers:
#   - 'log' to log normal process handling
#   - 'logres' to track system resource life
#   - 'logfix' to track wait/kill proxying in _ThreadFixer
log = logging.getLogger("process")
logres = logging.getLogger("process_res")
logfix = logging.getLogger("process_waitfix")

def _readRetryOnEINTR(fd, buffersize):
    """Like os.read, but retries on EINTR.
    
    From 'man 2 read':
        [EINTR]     A read from a slow device was interrupted before any
                    data arrived by the delivery of a signal.
    """
    while 1:
        try:
            return os.read(fd, buffersize)
        except OSError, e:
            if e.errno == errno.EINTR:
                continue
            else:
                raise

def _safeCreateProcess(avatar, appName, cmd, processSA, threadSA,
                       inheritHandles, creationFlags, env, cwd, si):

   new_env = {}
   if env is not None:
      for key, value in env.iteritems():
         new_env[unicode(key)] = unicode(value)
   env = new_env

   log.debug("""\
_SaferCreateProcess(appName=%r,
                 cmd=%r,
                 env=%r,
                 cwd=%r)
 os.getcwd(): %r
""", appName, cmd, env, cwd, os.getcwd())

   si.lpDesktop = r"winsta0\default"
   params = (appName, cmd, processSA, threadSA, inheritHandles,
             creationFlags, env, cwd, si)

   # If we have been given an avatar with credentials, create the
   # process as the identified user.
   if avatar is not None and avatar.mUserHandle is not None:
      # Run the command ase the authenticated user.
      user = avatar.mUserHandle
      win32security.ImpersonateLoggedOnUser(user)
      process, thread, process_id, thread_id\
         = win32process.CreateProcessAsUser(user, *params)
      win32security.RevertToSelf()
   else:
      process, thread, process_id, thread_id\
         = win32process.CreateProcess(*params)

   return process, thread, process_id, thread_id

class _FileWrapper:
   """Wrap a system file object, hiding some nitpicky details.
   
   This class provides a Python file-like interface to either a Python
   file object (pretty easy job), a file descriptor, or an OS-specific
   file handle (e.g.  Win32 handles to file objects on Windows). Any or
   all of these object types may be passed to this wrapper. If more
   than one is specified this wrapper prefers to work with certain one
   in this order:
       - file descriptor (because usually this allows for
         return-immediately-on-read-if-anything-available semantics and
         also provides text mode translation on Windows)
       - OS-specific handle (allows for the above read semantics)
       - file object (buffering can cause difficulty for interacting
         with spawned programs)

   It also provides a place where related such objects can be kept
   alive together to prevent premature ref-counted collection. (E.g. on
   Windows a Python file object may be associated with a Win32 file
   handle. If the file handle is not kept alive the Python file object
   will cease to function.)
   """
   def __init__(self, file=None, descriptor=None, handle=None):
      self.__log = log
      self._file = file
      self._descriptor = descriptor
      self._handle = handle
      self.mClosed = False
      if self._descriptor is not None or self._handle is not None:
         self._lineBuf = "" # to support .readline()

   def __del__(self):
      self.close()

   def __getattr__(self, name):
      """Forward to the underlying file object."""
      if self._file is not None:
          return getattr(self._file, name)
      else:
          raise ProcessError("no file object to pass '%s' attribute to"
                             % name)

   def _win32Read(self, nBytes):
      try:
         log.info("[%s] _FileWrapper.read: waiting for read on pipe",
            id(self))
         errCode, text = win32file.ReadFile(self._handle, nBytes)
      except pywintypes.error, ex:
         # Ignore errors for now, like "The pipe is being closed.",
         # etc. XXX There *may* be errors we don't want to avoid.
         log.info("[%s] _FileWrapper.read: error reading from pipe: %s",
                  id(self), ex)
         return ""
      assert errCode == 0,\
         "Why is 'errCode' from ReadFile non-zero? %r" % errCode
      if not text:
         # Empty text signifies that the pipe has been closed on
         # the parent's end.
         log.info("[%s] _FileWrapper.read: observed close of parent",
                  id(self))
         # Signal the child so it knows to stop listening.
         self.close()
         return ""
      else:
         log.info("[%s] _FileWrapper.read: read %d bytes from pipe: %r",
                  id(self), len(text), text)
      return text

   def read(self, nBytes=-1):
      if self._descriptor is not None:
         if nBytes <= 0:
            text, self._lineBuf = self._lineBuf, ""
            while 1:
               t = _readRetryOnEINTR(self._descriptor, 4092)
               if not t:
                  break
               else:
                  text += t
         else:
            if len(self._lineBuf) >= nBytes:
               text, self._lineBuf =\
                  self._lineBuf[:nBytes], self._lineBuf[nBytes:]
            else:
               nBytesToGo = nBytes - len(self._lineBuf)
               text = self._lineBuf \
                  + _readRetryOnEINTR(self._descriptor, nBytesToGo)
               self._lineBuf = ""
         return text
      elif self._handle is not None:
         if nBytes <= 0:
            text, self._lineBuf = self._lineBuf, ""
            while 1:
               t = self._win32Read(4092)
               if not t:
                  break
               else:
                  text += t
         else:
            if len(self._lineBuf) >= nBytes:
               text, self._lineBuf =\
                  self._lineBuf[:nBytes], self._lineBuf[nBytes:]
            else:
               nBytesToGo = nBytes - len(self._lineBuf)
               text, self._lineBuf =\
                  self._lineBuf + self._win32Read(nBytesToGo), ""
         return text
      else:   
         raise "FileHandle.read: no handle to read with"

   def readline(self):
      if self._descriptor is not None or self._handle is not None:
         while 1:
            #XXX This is not portable to the Mac.
            idx = self._lineBuf.find('\n')
            if idx != -1:
               line, self._lineBuf =\
                  self._lineBuf[:idx+1], self._lineBuf[idx+1:]
               break
            else:
               lengthBefore = len(self._lineBuf)
               t = self.read(4092)
               if len(t) <= lengthBefore: # no new data was read
                  line, self._lineBuf = t, ""
                  break
               else:
                  self._lineBuf += t
         return line
      else:
         raise "FileHandle.readline: no handle to read with"

   def readlines(self):
      if self._descriptor is not None or self._handle is not None:
         lines = []
         while 1:
            line = self.readline()
            if line:
               lines.append(line)
            else:
               break
         return lines
      elif self._file is not None:
         return self._file.readlines()
      else:
         raise "FileHandle.readline: no handle to read with"

   def write(self, text):
      try:
         errCode, nBytesWritten = win32file.WriteFile(self._handle, text)
      except pywintypes.error, ex:
         # Ingore errors like "The pipe is being closed.", for
         # now.
         log.info("[%s] _FileWrapper.write: error writing to pipe, "\
                  "ignored", id(self))
         return
      assert errCode == 0,\
             "Why is 'errCode' from WriteFile non-zero? %r" % errCode
      if not nBytesWritten:
         # No bytes written signifies that the pipe has been
         # closed on the child's end.
         log.info("[%s] _FileWrapper.write: observed close of pipe",
                  id(self))
         return
      else:
         log.info("[%s] _FileWrapper.write: wrote %d bytes to pipe: %r",
                  id(self), len(text), text)

   def close(self):
      """Close all associated file objects and handles."""
      #log.debug("[%s] _FileWrapper.close()", id(self))
      if not self.mClosed:
         self.mClosed = True
         if self._file is not None:
            #log.debug("[%s] _FileWrapper.close: close file", id(self))
            self._file.close()
            #log.debug("[%s] _FileWrapper.close: done file close", id(self))
         if self._handle is not None:
            #log.debug("[%s] _FileWrapper.close: close handle", id(self))
            try:
               win32api.CloseHandle(self._handle)
            except win32api.error:
               #log.debug("[%s] _FileWrapper.close: closing handle raised",
               #          id(self))
               pass
            #log.debug("[%s] _FileWrapper.close: done closing handle",
            #          id(self))

   def __repr__(self):
      return "<_FileWrapper: file:%r fd:%r os_handle:%r>"\
             % (self._file, self._descriptor, self._handle)


class Process:
   def __init__(self, cmd, mode='t', cwd=None, env=None, avatar = None):
      log.info("Process.__init__(cmd=%r, mode=%r, cwd=%r, env=%r)",
               cmd, mode, cwd, env)
      # Keep a reference to ensure it is around for this object's destruction.
      self.__log = log
      self.mCmd = cmd
      self.mCwd = cwd
      self.mEnv = env
      self.mAvatar = avatar
      self.mMode = mode
      if self.mMode not in ('t', 'b'):
         raise ProcessError("'mode' must be 't' or 'b'.")
      self.mClosed = False

      si = win32process.STARTUPINFO()
      si.dwFlags = (win32con.STARTF_USESTDHANDLES ^
                    win32con.STARTF_USESHOWWINDOW)

      # Create pipes for std handles.
      # (Set the bInheritHandle flag so pipe handles are inherited.)
      saAttr = pywintypes.SECURITY_ATTRIBUTES()
      saAttr.bInheritHandle = 1
      #XXX Should maybe try with os.pipe. Dunno what that does for
      #    inheritability though.
      hChildStdinRd, hChildStdinWr = win32pipe.CreatePipe(saAttr, 0) 
      hChildStdoutRd, hChildStdoutWr = win32pipe.CreatePipe(saAttr, 0) 
      hChildStderrRd, hChildStderrWr = win32pipe.CreatePipe(saAttr, 0) 

      try:
         # Duplicate the parent ends of the pipes so they are not
         # inherited. 
         hChildStdinWrDup = win32api.DuplicateHandle(
             win32api.GetCurrentProcess(),
             hChildStdinWr,
             win32api.GetCurrentProcess(),
             0,
             0, # not inherited
             DUPLICATE_SAME_ACCESS)
         win32api.CloseHandle(hChildStdinWr)
         self._hChildStdinWr = hChildStdinWrDup
         hChildStdoutRdDup = win32api.DuplicateHandle(
             win32api.GetCurrentProcess(),
             hChildStdoutRd,
             win32api.GetCurrentProcess(),
             0,
             0, # not inherited
             DUPLICATE_SAME_ACCESS)
         win32api.CloseHandle(hChildStdoutRd)
         self._hChildStdoutRd = hChildStdoutRdDup
         hChildStderrRdDup = win32api.DuplicateHandle(
             win32api.GetCurrentProcess(),
             hChildStderrRd,
             win32api.GetCurrentProcess(),
             0,
             0, # not inherited
             DUPLICATE_SAME_ACCESS)
         win32api.CloseHandle(hChildStderrRd)
         self._hChildStderrRd = hChildStderrRdDup

         # Set the translation mode and buffering.
         self._mode = 't'
         if self._mode == 't':
            flags = os.O_TEXT
         else:
            flags = 0
         fdChildStdinWr = msvcrt.open_osfhandle(self._hChildStdinWr, flags)
         fdChildStdoutRd = msvcrt.open_osfhandle(self._hChildStdoutRd, flags)
         fdChildStderrRd = msvcrt.open_osfhandle(self._hChildStderrRd, flags)

         self.stdin = _FileWrapper(descriptor=fdChildStdinWr,
                                   handle=self._hChildStdinWr)
         logres.info("[%s] Process._start(): create child stdin: %r",
                     id(self), self.stdin)
         self.stdout = _FileWrapper(descriptor=fdChildStdoutRd,
                                    handle=self._hChildStdoutRd)
         logres.info("[%s] Process._start(): create child stdout: %r",
                     id(self), self.stdout)
         self.stderr = _FileWrapper(descriptor=fdChildStderrRd,
                                    handle=self._hChildStderrRd)
         logres.info("[%s] Process._start(): create child stderr: %r",
                     id(self), self.stderr)


         si.hStdInput = hChildStdinRd
         si.hStdOutput = hChildStdoutWr
         si.hStdError = hChildStderrWr
         #si.wShowWindow = show
         si.wShowWindow = 1
         si.dwFlags |= win32process.STARTF_USESTDHANDLES

         creation_flags = win32process.CREATE_NEW_CONSOLE
         (self.mProcess, self.mThread, self.mProcessId, self.mThreadId)\
            = _safeCreateProcess(
               self.mAvatar,    # Avatar
               None,            # App name
               cmd,             # Command
               None,            # Process security attribs
               None,            # Primary thread security attribs
               1,               # Handles are inherited
               creation_flags,  # Creation Flags
               self.mEnv,       # Environment
               self.mCwd,       # Current Working Directory
               si)              # STARTUPINFO

      finally:
         # Close child ends of pipes on the parent's side (the
         # parent's ends of the pipe are closed in the _FileWrappers.)
         win32file.CloseHandle(hChildStdinRd)
         win32file.CloseHandle(hChildStdoutWr)
         win32file.CloseHandle(hChildStderrWr)

   def __del__(self):
      #XXX Should probably not rely upon this.
      #logres.info("[%s] ProcessOpen.__del__()", id(self))
      self.close()
      #del self.__log # drop reference

   def close(self):
      if not self.mClosed:
         self.__log.info("[%s] Process.close()" % id(self))

         # Ensure that all IOBuffer's are closed. If they are not, these
         # can cause hangs. 
         try:
            self.__log.info("[%s] Process: closing stdin (%r)."\
                            % (id(self), self.stdin))
            self.stdin.close()
         except AttributeError:
            # May not have gotten far enough in the __init__ to set
            # self.stdin, etc.
            pass
         try:
            self.__log.info("[%s] Process: closing stdout (%r)."\
                            % (id(self), self.stdout))
            self.stdout.close()
         except AttributeError:
            # May not have gotten far enough in the __init__ to set
            # self.stdout, etc.
            pass
         try:
            self.__log.info("[%s] Process: closing stderr (%r)."\
                            % (id(self), self.stderr))
            self.stderr.close()
         except AttributeError:
            # May not have gotten far enough in the __init__ to set
            # self.stderr, etc.
            pass

         self.mClosed = True

   def wait(self, mSec=None):
      """
      Wait for process to finish or for specified number of
      milliseconds to elapse.
      """
      if mSec is None:
         mSec = win32event.INFINITE
      return win32event.WaitForSingleObject(self.mProcess, mSec)

   def kill(self, gracePeriod=1000):
      """
      Kill process. Try for an orderly shutdown via WM_CLOSE.  If
      still running after gracePeriod (5 sec. default), terminate.
      """
      win32gui.EnumWindows(self.__close__, 0)
      if self.wait(gracePeriod) != win32event.WAIT_OBJECT_0:
         win32process.TerminateProcess(self.mProcess, 0)
         win32api.Sleep(100) # wait for resources to be released

   def __close__(self, hwnd, dummy):
      """
      EnumWindows callback - sends WM_CLOSE to any window
      owned by this process.
      """
      tid, pid = win32process.GetWindowThreadProcessId(hwnd)
      if pid == self.mProcessId:
         win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

   def exitCode(self):
      """
      Return process exit code.
      """
      return win32process.GetExitCodeProcess(self.mProcess)

if '__main__' == __name__:
   #p = Process(cmd="calc.exe")
   p = Process(cmd="cmd.exe /K dir")
   #p = Process(cmd="c:\\Program Files\\Infiscape\\Collab 0.2.0\\runGui.bat")
   line = p.stdout.readline()
   while line != '':
      print line
      print "Before"
      line = p.stdout.read(100)
      print "After"
   print "Waiting..."
   p.wait(1000)
   print "Done"
   #p.kill()
