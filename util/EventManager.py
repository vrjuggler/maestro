# Maestro is Copyright (C) 2006 by Infiscape
#
# Original Author: Aron Bierbaum
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import os, sys, os.path, traceback, types, weakref, time


class EventManager(object):
   """ Class to capture and handle event processing in the system.
       TODO:
         - Add culling of null references
   """
   def __init__(self):
      """ Initialize the event manager. """
      # Connections is a map of:
      #     node_guid: {signam, (slot callables,)}
      # the callable is held using a weak reference
      self.mConnections = {}
      self.mTimerHandler = TimerHandler()
      
   def update(self):
      """ Update method.  Called once per frame. """
      # Update timers
      self.mTimerHandler.callTimers()
   

   def connect(self, nodeId, sigName, slotCallable):
      """ Connect a signal to a slot (callable). 
          nodeId - GUID id of the node for the signal
          sigName - String name of the signal to monitor
          callable - A callable object taking whatever
                     parameters are required for the signal.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventManager.connect: nodeId of non-string type passed")
      if not isinstance(sigName, types.StringType):
         raise TypeError("EventManager.connect: sigName of non-string type passed")
      if not callable(slotCallable):
         raise TypeError("EventManager.connect: slotCallable of non-callable type passed")         
      
      # Make sure tables exist
      if not self.mConnections.has_key(nodeId):
         self.mConnections[nodeId] = {}
      if not self.mConnections[nodeId].has_key(sigName):
         self.mConnections[nodeId][sigName] = []
         
      callable_ref = WeakMethod(slotCallable)      
      self.mConnections[nodeId][sigName].append(callable_ref)

   def disconnect(self, nodeId, sigName, slotCallable):
      """ Disconnect a signal from a slot (callable). 
         Removes *all* found slots matching nodeId, sigName, slotCallable.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventManager.connect: nodeId of non-string type passed")
      if not isinstance(sigName, types.StringType):
         raise TypeError("EventManager.connect: sigName of non-string type passed")
      if not callable(slotCallable):
         raise TypeError("EventManager.connect: slotCallable of non-callable type passed")
      
      slot_callable = WeakMethod(slotCallable)
      
      if self.mConnections.has_key(nodeId):
         if self.mConnections[nodeId].has_key(sigName):
            slots = self.mConnections[nodeId][sigName]
            remove_items = []
            for x in range(len(slots)):
               assert isinstance(slots[x], (WeakMethodBound, WeakMethodFree))
               slot = slots[x]
               if (slot.isDead() or slot == slot_callable):
                  remove_items.append(x)
            remove_items.sort(reverse=True)  # Reverse so I can remove below
            
            for i in remove_items:
               assert i < len(slots)     # If this isn't true the sort or reverse failed
               del slots[i]
   
      
   def emit(self, nodeId, sigName, argsTuple=()):
      """ Emit the named signal on the given node.
          If there are no registered slots, just do nothing.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventManager.connect: nodeId of non-string type passed")
      if not isinstance(sigName, types.StringType):
         raise TypeError("EventManager.connect: sigName of non-string type passed")
      if not isinstance(argsTuple, types.TupleType):
         raise TypeError("EventManager.connect: argsTuple not of tuple type passed.")

      try:
         # Append out hostname to distinguish where messages are coming from.
         argsTuple = (nodeId,) + argsTuple

         print "DEBUG: EventManager.emit([%s][%s][%s])" % (nodeId, sigName, argsTuple)

         # If there are slots, loop over them and call
         if self.mConnections.has_key(nodeId):
            if self.mConnections[nodeId].has_key(sigName):
               for slot in self.mConnections[nodeId][sigName]:
                  assert isinstance(slot, (WeakMethodBound, WeakMethodFree))               
                  if not slot.isDead():
                     slot(*argsTuple)
                  else:
                     # remove slot
                     pass

         # If there are slots registered for all nodes, loop over them and call
         if self.mConnections.has_key("*"):
            if self.mConnections["*"].has_key(sigName):
               for slot in self.mConnections["*"][sigName]:
                  assert isinstance(slot, (WeakMethodBound, WeakMethodFree))               
                  if not slot.isDead():
                     slot(*argsTuple)
                  else:
                     # remove slot
                     pass
      except Exception, ex:
         print "ERROR: EventManager.emit(%s, %s, %s) [%s]" % (nodeId, sigName, argsTuple, ex)
         

   def timers(self):
      """ Return the timer handler class. """
      return self.mTimerHandler
   
   def _getConnections(self):
      return self.mConnections
   
   def _getCallables(self, nodeId, sigName):
      """ Return copy of list of callables for nodeId and sigName. """
      ret_val = []
      if self.mConnections.has_key(nodeId):
         if self.mConnections[nodeId].has_key(sigName):
            ret_val = self.mConnections[nodeId][sigName]
      return ret_val

# -------- Weak Method binding ------------ #
# Based on: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81253
#
class WeakMethodBound :
   def __init__( self , f ) :
      self.f = f.im_func
      self.c = weakref.ref( f.im_self )
   def __call__( self , *arg ) :
      if self.c() == None :
         raise TypeError , 'Method called on dead object'
      apply( self.f , ( self.c() , ) + arg )
   def isDead(self):
      return self.c() == None
   def __eq__(self, rhs):
      return (isinstance(rhs, WeakMethodBound) and               
              (self.f == rhs.f) and (self.c() == rhs.c()))
   def __hash__(self):
      return hash(self.f)
      # Don't know why this does not work.
      #return hash(self.f) + hash(self.c)

class WeakMethodFree :
   def __init__( self , f ) :
      self.f = weakref.ref( f )
   def __call__( self , *arg ) :
      if self.f() == None :
         raise TypeError , 'Function no longer exist'
      apply( self.f() , arg )
   def isDead(self):
      return self.f == None
   def __eq__(self, rhs):
      return (isinstance(rhs, WeakMethodBound) and               
              (self.f() == rhs.f()))
   def __hash__(self):
      return hash(self.f)

def WeakMethod( f ) :
   if hasattr(f,'im_func'):
      return WeakMethodBound( f )      
   else:
      return WeakMethodFree( f )   


# ------------------ Timer handler stuff ---------------- #
class TimerHandler(object):
   """ Holds list of all current timers. """
   
   class Timer(object):
      def __init__(self, cb, duration):         
         self.duration = duration
         self.slotRef = cb          # Callable ref
         if 0 == duration:
            self.nextTime = 0
         else:
            self.nextTime = time.time() + duration
   
   def __init__(self):
      " Constructor. "
      # map callable --> next_trigger_time
      #  - If trigger time == 0, then tigger always
      self.mTimerMap = {}
      
   def createTimer(self, slot, duration=0):
      """ Create a new timer.
          duration - number of seconds between triggers (float)
                     If zero, trigger every time
      """
      slot_ref = WeakMethod(slot)      
      self.mTimerMap[slot_ref] = TimerHandler.Timer(slot_ref, duration)
      
   def deleteTimer(self, slot):
      """ Delete any timer calling slot callable. """
      slot_ref = WeakMethod(slot)
      if self.mTimerMap.has_key(slot_ref):
         del self.mTimerMap[slot_ref]
   
   def callTimers(self):
      """ Call any timers that are ready. """
      null_keys = []    # track list of null refs to remove
      cur_time = time.time()
      
      for (slot_ref, timer) in self.mTimerMap.iteritems():         
         if slot_ref.isDead():               # Check for dead reference
            null_keys.append(slot_ref)
         else:
            next_time = timer.nextTime
            if next_time < cur_time:
               try:
                  slot_ref()               # Call the slot
               except Exception, ex:
                  err_text = "Error calling timer callback: %s\n  exception:"%slot_ref + str(ex)
                  print err_text
                  print "Removing slot."
                  traceback.print_exc()
                  null_keys.append(slot_ref)
               except:
                  print "Unknown exception in timer callback:"
                  traceback.print_exc()
                  null_keys.append(slot_ref)
               
               if 0 != next_time:       # Ignore zero since that is trigger always
                  timer.nextTime = timer.duration + cur_time
      
      # Clean up null keys
      for k in null_keys:
         del self.mTimerMap[k]
      
   
