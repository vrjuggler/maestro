cp process.py /usr/lib/python2.4/site-packages/
cp which.py /usr/lib/python2.4/site-packages/
cp SettingsService.py /usr/lib/python2.4/site-packages/
cp infclustercontrol /etc/rc.d/init.d/
cp infclustercontrold /usr/bin
chkconfig --add infclustercontrol
service infclustercontrol restart
