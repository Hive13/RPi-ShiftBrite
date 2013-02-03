import cherrypy

from iniparse import INIConfig

from .util.template import TemplatingFactory, render_template
from .util.navigation import NavigationFactory
from .util.authority import AuthorityFactory, AuthorityManager, Authority
from .util.display import *
from .util.hash import *

#-----------------------------------------------------------------------------
TemplatingFactory ().set_instance (InjectionTemplateManager ('./docs'))
NavigationFactory ().set_instance (AuthorityNavigationManager ('./data/menu.json'))
AuthorityFactory ().set_instance (AuthorityManager (Authority (['GUEST'])))

#-----------------------------------------------------------------------------
class WebInterface (object):
   """
      A graphical web interface to the RPi-ShiftBrite.
   """
   
   _cp_config = {"tools.sessions.on": True}

   def __init__ (self):
      self.config = INIConfig (open ('config.ini', 'r'))

   @cherrypy.expose
   def login (self, username, password):
      time.sleep (int (self.config.security.login_timeout))

   @cherrypy.expose
   def index (self):
      return "Hello, world!"


#-----------------------------------------------------------------------------
if __name__ == "__main__":
   cherrypy.quickstart (WebInterface (), config = 'cherrypy.conf')
