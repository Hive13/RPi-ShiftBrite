#-----------------------------------------------------------------------------
#
# Convenience methods for working with Mako templates.
#
# Author: Lee Supe
# Date: October 10th, 2012
#
# Released under the GNU General Public License, version 3.
#
#-----------------------------------------------------------------------------

import mako

from mako.template import Template
from mako.lookup import TemplateLookup

#-----------------------------------------------------------------------------
class TemplateException (Exception):
   def __init__ (self, message):
      Exception.__init__ (self, message)

#-----------------------------------------------------------------------------
class UndefinedValue (object):
   """
      A placeholder object for undefined template variables.
   """
   pass

mako.runtime.UNDEFINED = UndefinedValue ()

#-----------------------------------------------------------------------------
class TemplatingFactory (object):
   """
      A factory for maintaining a TemplateManager singleton.
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
         raise TemplateException ('No template manager has been configured.')

#-----------------------------------------------------------------------------
class TemplateManager (object):
   """
      Manages the template path and other related settings for templates.

      A singleton instance of this class is maintained in the template
      module for general usage.
   """
   
   def __init__ (self, dirs = None):
      if dirs is not None:
         self.set_lookup (TemplateLookup (dirs))
      else:
         self.set_lookup (None)

   def get_lookup (self):
      """
         Return the TemplateLookup object configured to retrieve templates.
      """
      if self.lookup is None:
         raise TemplateException ("No lookup has been defined, please call template.set_template_path before calling render_template.")

      return self.lookup

   def set_lookup (self, lookup):
      """
         Configure a TemplateLookup object to retrieve templates.
      """
      self.lookup = lookup

   def fetch_template (self, templateName):
      """
         Fetch a template from the template location.
      """
      return self.get_lookup ().get_template (templateName)

   def render_template (self, templateName, **kwargs):
      """
         Render a template from the template location with
         the given args.  Returns the string output of the
         template engine.
      """

      return self.fetch_template (templateName).render (**kwargs)

#-----------------------------------------------------------------------------
def render_template (filename, **kwargs):
   templateManager = TemplatingFactory ().get_instance ()
   return templateManager.render_template (filename, **kwargs)
