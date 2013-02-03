#-----------------------------------------------------------------------------
#
# Account: Utility classes for manipulating and gathering information
# regarding user and group accounts.
#
# Author: Lee Supe
# Date: October 25th, 2012
#
# Released under the GNU General Public License, version 3.
#
#-----------------------------------------------------------------------------

import cherrypy

from .authority import AuthorityFactory, Authority
from .template import TemplateManager, TemplatingFactory
from .navigation import NavigationManager, Menu, TYPE_MENU

from .hash import *

#-----------------------------------------------------------------------------
class AccountException (Exception):
   def __init__ (self, message):
      Exception.__init__ (self, message)

#-----------------------------------------------------------------------------
class User (object):
   def __init__ (username, password_hash, access_keys):
      self.username = username
      self.password_hash = password
      self.access_keys = access_keys

#-----------------------------------------------------------------------------
class UserAccountManager (object):
   """
      A class for querying user attributes from the database.
   """

   def __init__ (self, config):
      self.config = config
      self.users = read_users (config)

   def get_user (self, username):
      """
         Get the user identified by the given username.
         If no such user exists, None is returned.
      """

      if username in self.users:
         return self.users [username]
      else:
         return None

   def check_login (self, username, password):
      """
         Validate a login attempt given a username and salted password.
         Returns a User instance on success, and None on failure.
      """

      user = self.get_user (username)

      if user is None:
         return None
       
      passwordHash = hash_passwd (password, self.config.security.server_salt)
      
      if b64bin (passwordHash) == b64bin (user.password_hash):
         return user

      else:
         return None

   def get_access_keys (self, username):
      """
         Get all access keys for the given username.
      """
      
      user = self.get_user (username)

      if user is None:
         return []

      return user.access_keys

   def get_user_access_keys (self, username):
      """
         Get specifically the special access keys provided
         for the user, which may include access blocks.
      """
      
      user = self.get_user (username)

      if user is None:
         return []
      
      return accessKeys
   
   def get_current_user (self):
      """
         Get the currently logged in user, or None if there is none. 
      """

      return cherrypy.session.get ('user', None)

   def login (self, user):
      """
         Perform a user login, storing the given User instance in the
         session and acquiring all access keys for the given user.
      """
      
      authorityManager = AuthorityFactory ().get_instance ()
      authorityManager.set_authority (Authority (
         self.get_access_keys (user.username)))

      cherrypy.session ['user'] = user
   
   def logout (self):
      """
         Log the user out, removing the User instance from
         the session.
      """
      
      authorityManager = AuthorityFactory ().get_instance ()
      authorityManager.set_authority (None)

      cherrypy.session ['user'] = None

#-----------------------------------------------------------------------------
def read_users (config):
   """
      Read a list of users from an INIConfig structure.
      Users are identified by properties in the [user] group.
   """
   
   users = {}

   for username in config.users:
      user_params = config.users[username].split (":")
      users [username] = User (username, user_params[0], user_params[1].split (','))

   return users
