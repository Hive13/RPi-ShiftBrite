#-----------------------------------------------------------------------------
#
# Wrapper methods for common password hashing functionality.
#
# Author: Lee Supe
# Date: January 28th, 2013
#
# Released under the GNU General Public License, version 3.
#
#-----------------------------------------------------------------------------

from hashlib import sha512
from .binary import *

#-----------------------------------------------------------------------------
def hash_passwd (s, salt, iterations = 1, encoding = 'utf8'):
   digest = s

   for x in range (iterations):
      digest = b64str (sha512 (str_encode (digest + salt, encoding)).digest (), encoding)

   return digest
      

