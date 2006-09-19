# Copyright (C) Infiscape Corporation 2006

instance = None

NOVICE   = 100
ADVANCED = 101

class GlobalOptions:
   def __init__(self):
      global instance
      if instance is not None:
         raise self.error, "Only one global option object allowed."
      self.mOptions = {}
      self.mOptions["UserMode"] = NOVICE

instance = GlobalOptions()
