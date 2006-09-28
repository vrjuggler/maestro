# Reloader system
#
# Based on reloader recipe from the python cookbook.
#   See: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/160164
#
import weakref, inspect

class MetaInstanceTracker(type):
   """ Meta-class for tracking all instances. 
       @var __instance_refs__: List of weakref.ref()'s to current instances.
       
       New classes of this metatype get an extra __instance_refs__ class variable 
       (used to store weak references to instances) and an __instances__ method 
       (which strips dead references out of the __instance_refs__ list and returns 
       real references to the still live instances). When a class of metatype 
       MetaInstanceTracker is instantiated, a weak reference to the instances is 
       stored in the __instance_refs__ list.
   """
   def __new__(cls, name, bases, ns):
      t = super(MetaInstanceTracker, cls).__new__(cls, name, bases, ns)
      t.__instance_refs__ = []
      return t
   
   def __instances__(self):
      """ Returns a list of references to active instances.
      @postcondition: All weakrefs to deleted objects are freed.
      """
      instances = [(r, r()) for r in self.__instance_refs__]
      instances = filter(lambda (x,y): y is not None, instances)
      self.__instance_refs__ = [r for (r, o) in instances]
      return [o for (r, o) in instances]
   
   def __call__(self, *args, **kw):
      """ When class is constructed, store a weakref to it. """
      instance = super(MetaInstanceTracker, self).__call__(*args, **kw)
      #instance = super(MetaInstanceTracker, self).__call__()
      self.__instance_refs__.append(weakref.ref(instance))
      return instance

class InstanceTracker:
   """ Use this as base class if you just want instance tracking. """
   __metaclass__ = MetaInstanceTracker

class MetaAutoReloader(MetaInstanceTracker):
   """ Auto-reloader for classes.
   
   When the definition of a class of metatype MetaAutoReloader is executed (ie. a class call), 
   the namespace of the definition is examined to see if a class of the same 
   name already exists. If it does, then it is assumed that instead of a class 
   defintion, this is a class REdefinition, and all instances of the OLD class 
   (MetaAutoReloader inherits from MetaInstanceTracker, so they can easily be found) 
   are updated to the NEW class.
   """   
   def __new__(cls, name, bases, ns):
      new_class = super(MetaAutoReloader, cls).__new__(cls, name, bases, ns)
      f = inspect.currentframe().f_back
      for d in [f.f_locals, f.f_globals]:
         if d.has_key(name):
            old_class = d[name]
            for instance in old_class.__instances__():
               instance.change_class(new_class)
               new_class.__instance_refs__.append(
                  weakref.ref(instance))
            # this section only works in 2.3
            for subcls in old_class.__subclasses__():
               newbases = ()
               for base in subcls.__bases__:
                  if base is old_class:
                     newbases += (new_class,)
                  else:
                     newbases += (base,)
               subcls.__bases__ = newbases
            break
      return new_class

class AutoReloader:
   """ Classes derived from autoReloader will auto-matically replace all instances 
       in memory when a new class call is seen (when the module is reloaded).
   """
   __metaclass__ = MetaAutoReloader
   def change_class(self, new_class):
      self.__class__ = new_class

