#-----------------------------------------------------------------------------
#
# A module of useful methods for working with byte strings
# and converting them to and from UTF-8 strings.
#
# Author: Lee Supe
# Date: September 24th, 2012
#
# Released under the GNU General Public License, version 3.
#
#-----------------------------------------------------------------------------

import base64

#-----------------------------------------------------------------------------
def b64bin (s, encoding='utf8'):
   """
      Converts the given base64 string to a raw byte string.
   """

   return base64.b64decode (s.encode (encoding))

#-----------------------------------------------------------------------------
def b64str (b, encoding='utf8'):
   """
      Converts the given raw byte string into a base64 string.
   """

   return base64.b64encode (b).decode (encoding)
