#-----------------------------------------------------------------------------
#
# Navigation: Classes and decorators to orchestrate navigation 
# and workflow in a CherryPy application.
#
# Author: Lee Supe
# Date: October 18th, 2012
#
# Released under the GNU General Public License, version 3.
#
#-----------------------------------------------------------------------------

import cherrypy

from .data import parse_json

#-----------------------------------------------------------------------------
# Menu node type constants.
#
TYPE_MENU = 'M'
TYPE_ACTION = 'A'
TYPE_SEPARATOR = 'S'

#-----------------------------------------------------------------------------
class NavigationException (Exception):
   def __init__ (self, message):
      Exception.__init__ (self, message)

#-----------------------------------------------------------------------------
class Node (object):
   """
      A base class for navigation nodes.
   """

   def __init__ (self, typeName, name, access = "*"):
      self.typeName = typeName
      self.name = name
      self.access = access

#-----------------------------------------------------------------------------
class Menu (Node):
   """
      A menu containing navigation nodes.
   """

   def __init__ (self, name, items = [], access = "*"):
      Node.__init__ (self, TYPE_MENU, name, access)
      self.items = []
      for node in items:
         self.items.append (node)

#-----------------------------------------------------------------------------
class Action (Node):
   """
      An menu node which activates a function or links
      to another resource.
   """

   def __init__ (self, name, url, desc = '', access = "*"):
      Node.__init__ (self, TYPE_ACTION, name, access)
      self.url = url
      self.desc = desc

#-----------------------------------------------------------------------------
class Separator (Node):
   """
      A node representing a separation of context in menu items.
   """

   def __init__ (self):
      Node.__init__ (self, SEPARATOR, 'Separator')

#-----------------------------------------------------------------------------
def loadFromJSON (filename):
   """
      Loads a navigation hierarchy from a JSON file.
   """
   
   def menuFromJSON (name, items, access = '*'):

      menu = Menu (name, [], access)
      
      for item in items:
         if 'items' in item:
            print ('menu item dict = %s' % repr (item))
            menu.items.append (menuFromJSON (**item))
         elif 'url' in item:
            menu.items.append (Action (**item))
         elif item == 'Separator':
            menu.items.append (Separator ())
         else:
            raise NavigationException ("Invalid value while processing menu JSON.")

      return menu

   jsonData = parse_json (filename)

   menus = [menuFromJSON (**menuData) for menuData in jsonData['items']]
   
   menusDict = {}

   for menu in menus:
      menusDict [menu.name] = menu
   
   return menusDict

#-----------------------------------------------------------------------------
class NavigationFactory (object):
   """
      A factory for maintaining a NavigationManager singleton.
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
         raise NavigationException ('No navigation manager has been configured.')

#-----------------------------------------------------------------------------
class NavigationManager (object):
   """
      Manages menus definitions loaded from a given JSON file.
   """

   def __init__ (self, jsonFileName = None):
      if jsonFileName is not None:
         try:
            self.menus = loadFromJSON (jsonFileName)
         except Exception as excVal:
            raise NavigationException ("Could not load navigation file '%s': %s" % (
               jsonFileName, excVal))

   def get_menu (self, menuName):
      if not menuName in self.menus:
         raise NavigationException ("No menu named '%s' is defined." % menuName)
      
      return self.menus [menuName]

   def present_menu (self, menu, groupName = 'main'):
      """
         Adds the given menu to the cherrypy.request object's collection
         of menus to be displayed for the given menu group.
      """
      
      if not hasattr (cherrypy.request, 'nav'):
         cherrypy.request.nav = {}

      if not groupName in cherrypy.request.nav:
         cherrypy.request.nav [groupName] = []
      
      for item in menu.items:
         cherrypy.request.nav [groupName].append (item)

