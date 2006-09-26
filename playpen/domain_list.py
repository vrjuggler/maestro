import wmi

c = wmi.WMI()
for i in c.Win32_NTDomain():
   print i
