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

def addLicense(source, target, env):
   if os.path.exists(source[0].path):
      f = open(source[0].path, 'r')
      lines = f.readlines()
      f.close()
      lines = [line for line in lines if not line.startswith('#')]
      lines[:0] = license
      f = open(source[0].path, 'w+')
      f.writelines(lines)

# Pyuic builder
def registerPyuicBuilder(env):
  pyuic_build_str = 'pyuic4 -x -i3 $SOURCE -o $TARGET'
  pyuic_builder = Builder(action = pyuic_build_str,
                          src_suffix = '.ui',
                          suffix = '.py')

  pyuic_license = SCons.Builder.MultiStepBuilder(action=SCons.Action.Action(addLicense),
                                            src_builder = pyuic_builder,
                                            src_suffix = '.py')

  env.Append(BUILDERS = {'Pyuic' : pyuic_license})

  pyrcc_build_str = 'pyrcc4 -compress 5 $SOURCE -o $TARGET'
  pyrcc_builder = Builder(action = pyrcc_build_str,
                          src_suffix = '.qrc',
                          suffix = '.py')
  pyrcc_license = SCons.Builder.MultiStepBuilder(action=SCons.Action.Action(addLicense),
                                            src_builder = pyrcc_builder,
                                            src_suffix = '.py')


  env.Append(BUILDERS = {'Pyrcc' : pyrcc_license})


env = Environment(ENV=os.environ)

registerPyuicBuilder(env);    # Register custom builders


opts = Options(files = ['options.cache', 'options.custom']);  # Add options



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
