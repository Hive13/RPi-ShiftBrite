#-----------------------------------------------------------------------------
#
# Custom: Extensions of utility classes for use in CherryPy webapps.
#
# Author: Lee Supe
# Date: October 23rd, 2012
#
# Released under the GNU General Public License, version 3.
#
#-----------------------------------------------------------------------------

import cherrypy

from .authority import AuthorityFactory
from .template import TemplateManager, TemplatingFactory
from .navigation import NavigationFactory, NavigationManager, Menu, TYPE_MENU

#-----------------------------------------------------------------------------
class AuthorityNavigationManager (NavigationManager):
   """
      A navigation manager which filters menus based on access
      points in the cherrypy.session.
   """
   
   def __init__ (self, jsonFileName = None):
      super (AuthorityNavigationManager, self).__init__ (jsonFileName)
   
   def get_menu (self, menuName):
      menu = super (AuthorityNavigationManager, self).get_menu (menuName)
      
      authority = AuthorityFactory ().get_authority ()
      return self.filter_menu (menu, authority)

   def filter_menu (self, menu, authority):
      """
         Filters the given menu via access points in the
         given Authority instance.
      """
      
      filteredMenuItems = []
      
      for item in menu.items:
         if item.access == '*' or authority.check (item.access):
            if item.typeName == TYPE_MENU:
               filteredMenuItems.append (self.filter_menu (item, authority))
            else:
               filteredMenuItems.append (item)
      
      filteredMenu = Menu (menu.name, filteredMenuItems, menu.access)
      
      return filteredMenu

   def present_menu (self, menu, groupName = 'main'):
      super (AuthorityNavigationManager, self).present_menu (menu, groupName)

      templateManager = TemplatingFactory ().get_instance ()
      templateManager.inject_param ('nav', cherrypy.request.nav)

#-----------------------------------------------------------------------------
class InjectionTemplateManager (TemplateManager):
   """
      An extension of TemplateManager which attempts to inject
      extra keyword variables into the evaluation of templates.
      
      Injected parameters are stored with the cherrypy.request
      object, thus they do not persist across requests.
   """

   def __init__ (self, dirs = None):
      super (InjectionTemplateManager, self).__init__ (dirs)
   
   def inject_param (self, param_name, value):
      """
         Injects the given parameter name into template rendering.
      """

      if not hasattr (cherrypy.request, 'template_injections'):
         cherrypy.request.template_injections = {}

      cherrypy.request.template_injections [param_name] = value
   
   def get_injected_params (self):
      """
         Get any injected parameters off of the cherrypy.request.   
      """

      if hasattr (cherrypy.request, 'template_injections'):
         return cherrypy.request.template_injections
      
      else:
         return {}

   def render_template (self, templateName, **kwargs):
      """
         Render a template from the template location with
         the given args, and any injected arguments.
         Returns the string output of the template engine.
      """

      kwargs.update (self.get_injected_params ())
      return super (InjectionTemplateManager, self).render_template (templateName, **kwargs)

#-----------------------------------------------------------------------------
def display_menu (menuName, groupName = 'main'):
   navigationManager = NavigationFactory ().get_instance ()
   menu = navigationManager.get_menu (menuName)
   navigationManager.present_menu (menu, groupName)

#-----------------------------------------------------------------------------
def display_message (message):
   templateManager = TemplatingFactory ().get_instance ()
   injected_params = templateManager.get_injected_params ()
   notifications = []

   if 'notifications' in injected_params:
      notifications = injected_params ['notifications']

   notifications.append (message)
   templateManager.inject_param ('notifications', notifications)

