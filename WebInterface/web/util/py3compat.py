#-----------------------------------------------------------------------------
#
# py3compat: Methods for dealing with python3 compatibility issues.
#
# Author: Lee Supe
# Date: October 10th, 2012
#
# Released under the GNU General Public License, version 3.
#
#-----------------------------------------------------------------------------

import sys

#-----------------------------------------------------------------------------
def read_input ():
   """
      Read a line of input from stdin.  Python 3 moves the behavior of
      raw_input to input, while input in Python 2 evaluates an expression.
   """

   if sys.version_info [0] < 3:
      return raw_input ()
   else:
      return input ()
