#-----------------------------------------------------------------------------
#
# A module of methods for mapping various representative data formats
# onto python objects, methods, and data structures.
#
# Author: Lee Supe
# Date: September 24th, 2012
#
# Released under the GNU General Public License, version 3.
#
# parse_json comment filtering courtesy of Daimen Riquet
#     http://www.lifl.fr/~riquetd/
#
#-----------------------------------------------------------------------------

import json
import types
import re
import collections

# Regular expression for comments in a JSON file.
JSON_COMMENT_RE = re.compile (
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)

#-----------------------------------------------------------------------------
def parse_json (filename, ordered = True):
    """ 
      Parses a JSON file which may contain comments.
      The json package methods do not support comments in input data...

      Objects in the JSON file are loaded as OrderedDicts
      with keys in file order.
    """

    with open (filename) as f:
      content = ''.join (f.readlines ())

      # Looking for comments
      match = JSON_COMMENT_RE.search (content)
      while match:
         # single line comment
         content = content[:match.start ()] + content[match.end ():]
         match = JSON_COMMENT_RE.search (content)

      # Parse JSON file.
      jsonData = None
      if ordered:
         jsonData = json.loads (content, object_hook = collections.OrderedDict)

      else:
         jsonData = json.loads (content)

      return jsonData

#-----------------------------------------------------------------------------
def json_listmap (jsonFilename, func):
   """
      Maps the list of lists loaded from the given json filename
      to the callable 'func' provided and returns a list of the results.
   """
   
   jsonData = []
   resultList = []

   jsonData = parse_json (jsonFilename)

   for jsonList in jsonData:
      resultList.append (func (*jsonList))

   return resultList

#-----------------------------------------------------------------------------
def glob_load (fileGlob, func, listLoaderProc = json_listmap):
   """
      Maps the lists of lists loaded from each filename matching the
      given glob, yielding the contents of one list of lists at a time.
   """

   for filename in glob.iglob (jsonGlob):
      resultList = listLoaderProc (filename)

      for result in resultList:
         yield result

#-----------------------------------------------------------------------------
def JSONLoad (cls):
   """
      A class decorator, adding a 'loadJSON' static method to the class
      mapping the class' constructor to a list of lists from a JSON file.
   """
   def loadJSON (filename):
      """
         Returns a list of objects from a JSON file.
         See json_listmap for more details.
      """
      
      return json_listmap (filename, cls)

   
   setattr (cls, 'loadJSON', staticmethod (loadJSON))

   return cls
