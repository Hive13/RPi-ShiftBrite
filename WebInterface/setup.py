#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Configuration setup script for RPi-ShiftBrite
#
# Author: Lee Supe
# Date: February 3rd, 2013
#
# Released under the GNU General Public License, version 3.
#-----------------------------------------------------------------------------

import sys
import os
import getopt
import traceback
import random

from iniparse import INIConfig
from web.util.hash import *

#-----------------------------------------------------------------------------
SHORTOPTS = 'fc:'
LONGOPTS  = ['force', 'config=']

#-----------------------------------------------------------------------------
def main (argv):
   configFilename = 'config.ini'
   forceSetup = 0

   config = None

   opts, args = getopt.getopt (argv, SHORTOPTS, LONGOPTS)

   for opt, val in opts:
      if opt in ['-f', '--force']:
         forceCreation += 1

      elif opt in ['-c', '--config']:
         configFilename = str (val)
   
   try:
      config = INIConfig (open (configFilename, 'r'))

   except:
      print ("Could not read input config file: %s." % configFilename)
      traceback.print_exc ()
      print ("Aborting.")
      sys.exit (1)
   
   print ("Deleting any existing users...")

   try:
      del config.user
      if not forceSetup:
         print ("There are users configured in \'%s\'!  Please create a backup of this file before running setup.  To overwrite the file in place, use --force." % configFilename)
         print ("Aborting.")
         sys.exit (1)
         
      print ("All users deleted.")

   except:
      print ("No users exist.")

   # TODO: Create an admin user, print the password, and save the configs.

#-----------------------------------------------------------------------------
if __name__ == "__main__":
   main (sys.argv [1:])
