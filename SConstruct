#!python
# SCons based build file for the property template crap
# Base file
import SCons;
import sys;
import os;
import string;
#import wing.wingdbstub;       # stuff for debugging
import SConsAddons.Util as sca_util

pj = os.path.join;

# Pyuic builder
def registerPyuicBuilder(env):
  #pyuic_build_str = 'pyuic4 -x -i3 -o $TARGET $SOURCE';
  pyuic_build_str = 'pyuic4 -x -i3 $SOURCE -o $TARGET';
  pyuic_builder = Builder(action = pyuic_build_str,
                          src_suffix = '.ui',
                          suffix = '.py');                            env.Append(BUILDERS = {'Pyuic' : pyuic_builder});

  #pyuic_build_str = 'pyrcc4 -compress 5 -o $TARGET $SOURCE';
  pyuic_build_str = 'pyrcc4 -compress 5 $SOURCE -o $TARGET';
  pyuic_builder = Builder(action = pyuic_build_str,
                          src_suffix = '.qrc',
                          suffix = '.py');                            env.Append(BUILDERS = {'Pyrcc' : pyuic_builder});
  #pyuic_build_str = 'pyuic4 -x -i3 -subimpl ${TARGET.filebase} -o $TARGET $SOURCE';
  #pyuic_builder = Builder(action = pyuic_build_str,
  #                        src_suffix = '.ui',
  #                        suffix = '.py');                            env.Append(BUILDERS = {'PyuicImpl' : pyuic_builder});


# ###############################
# Create builder
# ###############################

env = Environment(ENV=os.environ)

registerPyuicBuilder(env);    # Register custom builders


opts = Options(files = ['options.cache', 'options.custom']);  # Add options

license = \
"""#!/bin/env python

# Maestro is Copyright (C) 2006 by Infiscape
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

def removeComments(path):
   f = open(path, 'r')
   lines = f.readlines()
   f.close()
   lines = [line for line in lines if not line.startswith('#')]
   lines[:0] = license
   f = open(path, 'w+')
   f.writelines(lines)

# Python UI files
pyuic_src_files = []
for path, dirs, files in sca_util.WalkBuildFromSource('.',env):
   pyuic_src_files += [pj(path,f) for f in files if f.endswith('.ui')]

#print pyuic_src_files

pyuic_rc_files = []
for path, dirs, files in sca_util.WalkBuildFromSource('.',env):
   pyuic_rc_files += [pj(path,f) for f in files if f.endswith('.qrc')]

#print pyuic_rc_files

generated_entries = {}
for sfile in pyuic_src_files:
   generated_entries += env.Pyuic(sfile)
for sfile in pyuic_rc_files:
   generated_entries += env.Pyrcc(sfile)

for entry in generated_entries:
   removeComments(entry.path)


Default(".");
Help(help_text); 
