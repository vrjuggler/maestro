# Windows Internals Page 272


# Notes: CONNECT_CMD_SAVECRED

import win32con
import registry

user_reg = registry.RegistryDict(win32con.HKEY_CURRENT_USER)

for k,v in user_reg['Network'].iteritems():
   print "Network Drive: [%s] %s" % (k,v)
