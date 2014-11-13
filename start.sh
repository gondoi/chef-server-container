#!/bin/bash
/opt/chef-server/embedded/bin/runsvdir-start &
sleep 10
tail -F /var/log/chef-server/**/current &
python /root/chef_proxy.py
