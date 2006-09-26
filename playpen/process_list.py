import wmi
c = wmi.WMI ()
for process in c.Win32_Process ():
   (domain, return_value, user) = process.GetOwner()
   print process.ProcessId, process.Name, user
