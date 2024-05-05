#!/bin/bash

K1_IP_ADDR=192.168.32.253

scp custom_macro.py root@${K1_IP_ADDR}:/usr/share/klipper/klippy/extras
scp gcode_macro.cfg root@${K1_IP_ADDR}:/usr/data/printer_data/config
ssh root@${K1_IP_ADDR} /etc/init.d/S55klipper_service restart
