service infclustercontrol stop
chkconfig --del infclustercontrol

rm /usr/lib/python2.4/site-packages/process.py
rm /usr/lib/python2.4/site-packages/which.py
rm /usr/lib/python2.4/site-packages/SettingsService.py
rm /etc/rc.d/init.d/infclustercontrol
rm /usr/bin/infclustercontrold
rm /var/log/infclustercontrold.log
