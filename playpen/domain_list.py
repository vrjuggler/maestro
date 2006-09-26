import wmi

print "Making a WMI connection..."
c = wmi.WMI()
print "Have a WMI connection..."

for comp in c.Win32_ComputerSystem():
   print "ComputerName: ", comp.Name
   print "UserName:", comp.UserName
   print "PartOfDomain: ", comp.PartOfDomain
   print "Domain: ", comp.Domain


print "Finding all domains: "
for i in c.Win32_NTDomain():
   print i
