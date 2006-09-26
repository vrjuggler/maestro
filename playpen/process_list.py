import wmi
c = wmi.WMI ()
for process in c.Win32_Process ():
   (domain, return_value, user) = process.GetOwner()
   if process.CreationDate is not None:
      time_tuple = wmi.to_time(process.CreationDate)
      real_time = "%02d/%02d/%d %d:%02d:%02d" % (time_tuple[1], time_tuple[2], time_tuple[0],
         time_tuple[3], time_tuple[4], time_tuple[5])
   else:
      real_time = ""
   print process.Name, process.ProcessId, process.ParentProcessId, user, real_time, process.CommandLine
