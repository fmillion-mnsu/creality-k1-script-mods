#!/bin/bash

# This will install the script files to a rooted K1.

# You either need to provide your K1's root password THREE times,
# or you can make it better by adding your machine's public SSH
# key to the authorized_keys file in /root/.ssh on the K1.

K1_IP_ADDR=192.168.32.253

scp custom_macro.py root@${K1_IP_ADDR}:/usr/share/klipper/klippy/extras
scp gcode_macro.cfg root@${K1_IP_ADDR}:/usr/data/printer_data/config
ssh root@${K1_IP_ADDR} /etc/init.d/S55klipper_service restart
