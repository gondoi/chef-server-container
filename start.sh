#!/bin/bash
if [ ! -f /etc/chef-server/admin.pem ]; then
  /opt/chef-server/embedded/bin/runsvdir-start &
  chef-server-ctl reconfigure
fi
/opt/chef-server/embedded/bin/runsvdir-start &
sleep 10
tail -F /var/log/chef-server/**/current &
python /root/chef_proxy.py
