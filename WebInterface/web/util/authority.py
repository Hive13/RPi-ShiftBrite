#-----------------------------------------------------------------------------
#
# Authority: Classes and decorators to address
# authorization of accessKeys in a CherryPy application.
#
# Author: Lee Supe
# Date: September 24th, 2012
#
# Released under the GNU General Public License, version 3.
#
#-----------------------------------------------------------------------------

import cherrypy

#-----------------------------------------------------------------------------
class AccessDeniedException (cherrypy._cperror.HTTPError):
   def __init__ (self, message):
      cherrypy._cperror.HTTPError.__init__ (self, "403 Forbidden", message)

#-----------------------------------------------------------------------------
class Authority (object):
   """
      A class representing and communicating what a user can do
      in the system.  These possible accessKeys are represented by
      access keys.
   """

   def __init__ (self, accessKeys):
      """
         Initializes the Authority instance with a list of available
         access keys.
      """

      self.accessKeys = self._reconcile_access_blocks (set (accessKeys))
   
   def check (self, action):
      """
         Check to see if the given access key is available.
      """
      
      return action in self.accessKeys

   def check_all (self, accessKeys):
      """
         Check each action in the given list to confirm
         that it is in the list of available accessKeys.
         Return False if any of the listed accessKeys
         are not avaialble.
      """

      for action in accessKeys:
         if not self.check (action):
            return False

      return True

   def _reconcile_access_blocks (self, accessKeySet):
      """
         Reconcile any access key blocks in the key set.
         A key matching '^ACTION' will cause the specified
         action to be removed.

         A key starting with more than one '^' will cause
         an AuthorityException.
      """
      
      newKeySet = set ()

      for key in accessKeySet:
         newKeySet.add (key)

      for key in accessKeySet:
         if key[:1] == '^':
            targetKey = key [1:]
            if targetKey[:1] == '^':
               raise AuthorityException ("Cannot block an access key block: %s." % key)

            newKeySet.remove (targetKey)
            newKeySet.remove (key)

      return newKeySet

#-----------------------------------------------------------------------------
class AuthorityFactory (object):
   """
      A factory object maintaining an AuthorityManager singleton.
   """

   __shared_state = {}

   def __init__ (self):
      self.__dict__ = self.__shared_state

   def set_instance (self, instance):
      self.instance = instance

   def get_instance (self):
      try:
         return self.instance
      except AttributeError:
         raise AuthorityException ('No authority manager has been configured.')

   def get_authority (self):
      return self.get_instance ().get_authority ()

#-----------------------------------------------------------------------------
class AuthorityManager (object):
   """
      An object to manage and maintain Authority instances.
   """

   def __init__ (self, defaultAuthority):
      self.defaultAuthority = defaultAuthority

   def get_authority (self):
      """
         Gets the current session's Authority instance, or returns
         the default authority instance if none is available.
      """

      authority = cherrypy.session.get ('__authority', None)

      if authority is None:
         return self.defaultAuthority
      else:
         return authority

   def set_authority (self, authority):
      """
         Sets the current session's Authority instance.
      """

      cherrypy.session ['__authority'] = authority

#-----------------------------------------------------------------------------
class Access (object):
   """
      A method decorator for CherryPy.

      This decorator modifies the method so that the current session's
      Authority instance is checked for access to the access keys
      specified in 'accessKeys'.

      If the Authority instance does not have access to the access keys,
      an AccessDeniedException is thrown.
   """
   
   def __init__ (self, *accessKeys, **kwargs):
      self.actionKeys = accessKeys

   def __call__ (self, f):
      if not hasattr (f, '_cp_config'):
         f._cp_config = dict ()

      if '__access_keys' not in f._cp_config:
         f._cp_config['__access_keys'] = []

      f._cp_config['__access_keys'].extend (self.actionKeys)

      return f

#-----------------------------------------------------------------------------
def check_auth (*args, **kwargs):
   """
      A cherrypy tool that looks in the request config for '__access_keys'
      containing a list of access keys.  If it exists, the current session's
      Authority instance is checked for each access key.  If any keys are
      missing from the Authority instance or there is no Authority instance,
      an AccessDeniedException is thrown.
   """
   
   authority = AuthorityFactory ().get_authority ()
   actionKeys = cherrypy.request.config.get ('__access_keys', None)

   if actionKeys is not None:
      if not authority.check_all (actionKeys):
         raise AccessDeniedException ('Access denied.')

#-----------------------------------------------------------------------------
cherrypy.tools.authority = cherrypy.Tool ('before_handler', check_auth)

