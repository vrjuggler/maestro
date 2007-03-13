#!python
import sys, os, re, string
import SCons
import SConsAddons.Util as sca_util

pj = os.path.join;


license = \
"""# Maestro is Copyright (C) 2006-2007 by Infiscape
#
# Original Author: Aron Bierbaum
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""

def addLicense(source):
   if os.path.exists(source):
      f = open(source, 'r')
      lines = f.readlines()
      f.close()

      f = open(source, 'w+')
      f.write(license)

      for l in lines:
         f.write(l)

      f.close()

def runPyuic(target = None, source = None, env = None):
   ui_file = str(source[0])
   py_file = str(target[0])
   pyuic_build_str = 'pyuic4 -x -i3 %s -o %s' % (ui_file, py_file)
   status = Execute(pyuic_build_str)

   if status == 0:
      addLicense(py_file)

   return status

def registerPyuicBuilder(env):
   pyuic_builder = Builder(action = Action(runPyuic), src_suffix = '.ui',
                           suffix = '.py')
   env.Append(BUILDERS = {'Pyuic' : pyuic_builder})

def runPyrcc(target = None, source = None, env = None):
   qrc_file = str(source[0])
   py_file  = str(target[0])
   pyrcc_build_str = 'pyrcc4 -compress 5 %s -o %s' % (qrc_file, py_file)
   status = Execute(pyrcc_build_str)

   if status == 0:
      addLicense(py_file)

   return status

def registerPyrccBuilder(env):
   # Translate filename.qrc to filename_rc.py. For whatever reason, pyuic4
   # adds an 'import filename_rc' line (rather than 'import filename' for each
   # referenced .qrc file. Therefore, we have to be sure to generate a Python
   # file with the correct name so that no post processing of files genertec
   # by pyuic4 is needed.
   def qrcEmitter(target, source, env):
      for i in range(len(source)):
         target[i] = os.path.splitext(str(source[i]))[0] + '_rc.py'
      return (target, source)

   # Extract implicit dependencies from .qrc files.
   def qrcScanner(node, env, path):
      qrc_file = str(node)
      deps = []

      if os.path.exists(qrc_file):
         file_re = re.compile('<file>(.*?)</file>')

         f = open(qrc_file, 'r')
         contents = f.read()
         f.close()

         base_dir = os.path.split(qrc_file)[0]
         files = file_re.findall(contents)
         for f in files:
            dep_file = os.path.join(base_dir, f)

            # Here, we test to see if f exists relative to base_dir. This is
            # needed to contend with the current working directory for scons.
            # If f does exist, then we add it to deps without base_dir
            # prepdended, once again to deal with scons behavior.
            if os.path.exists(dep_file):
               deps.append(f)
            
      return deps

   pyrcc_builder = Builder(action = Action(runPyrcc), src_suffix = '.qrc',
                           suffix = '.py', emitter = qrcEmitter,
                           source_scanner = Scanner(function = qrcScanner))

   env.Append(BUILDERS = {'Pyrcc' : pyrcc_builder})

env = Environment(ENV=os.environ)

# Register custom builders
registerPyuicBuilder(env)
registerPyrccBuilder(env)

opts = Options(files = ['options.cache', 'options.custom'])     # Add options

# Python UI files
pyuic_src_files = []
for path, dirs, files in sca_util.WalkBuildFromSource('.',env):
   pyuic_src_files += [pj(path,f) for f in files if f.endswith('.ui')]

#print pyuic_src_files

pyuic_rc_files = []
for path, dirs, files in sca_util.WalkBuildFromSource('.',env):
   pyuic_rc_files += [pj(path,f) for f in files if f.endswith('.qrc')]

#print pyuic_rc_files

for sfile in pyuic_src_files:
   env.Pyuic(sfile)
for sfile in pyuic_rc_files:
   env.Pyrcc(sfile)

Default(".");
