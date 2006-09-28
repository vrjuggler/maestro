# mixins

# Implementation of singleton and borg patterns.
# both of these support derivation.
#
# The difference is that Singleton returns the same instance each time
# so the instances test == to each other.
#
# Borg creates new instances that just share state
#

class Singleton(object):
   """ Note, the init method will be called multiple times. """
   def __new__(ctype):
      if not '_the_instance' in ctype.__dict__:
         ctype._the_instance = object.__new__(ctype)
      return ctype._the_instance

class Borg(object):   
   """ Note, the init method will be called multiple times. """
   def __new__(ctype):
      self = object.__new__(ctype)
      if not '_state' in ctype.__dict__:
         ctype._state = {}
      self.__dict__ = ctype._state
      return self

