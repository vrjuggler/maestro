import threading
import select

class LogThread(threading.Thread):
   """
   Handles reading output from a running command so that the main GUI
   thread can display it.
   """
   def __init__(self, stdout, queue, doneCallback):
      threading.Thread.__init__(self)

      self.mStdout   = stdout
      self.mKeepRunning = False
      self.mQueue = queue
      self.mDoneCallback = doneCallback

   def run(self):
      self.mKeepRunning = True

      count = 0
      while self.mKeepRunning and not self.mStdout.closed:

         # We only care about the output list.
         input_list, output_list, ex_list = select.select([], [self.mStdout], [self.mStdout], 0.5)

         # This is here for debugging purposes at this time.
         if len(ex_list) > 0:
            print "Exceptional state detected"
            if ex_list[0] == self.cmdStdout:
               print "Exceptional state"
               break

         if len(output_list) > 0:
            for d in output_list:

               # This blocks until there is output to read.  Since we know
               # from the select() call above there is something to read,
               # this should never block.
               l = self.mStdout.readline()

               # If nothing was read, the thread can exit.
               if l == "":
                  self.mKeepRunning = False
                  # Send to tell thread to exit.
                  self.mQueue.put(l)
               else:
                  self.mQueue.put(l)
                  print "DEBUG %d: %s" % (count, l),
                  count += 1

      # This will cause the running application to exit.
      self.mStdout.close()

      # Tell our owner that we're closing down the shop.
      self.mDoneCallback()

      print "Thread Done"

   def abort(self):
      """
      Tells this thread to stop reading from the command.

      At this time, this method does not know how to kill the spawned process
      that is generating the output.
      """
      self.mKeepRunning = False
