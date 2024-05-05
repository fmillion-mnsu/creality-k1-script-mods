#!/bin/bash

scp custom_macro.py root@192.168.32.253:/usr/share/klipper/klippy/extras
scp gcode_macro.cfg root@192.168.32.253:/usr/data/printer_data/config
ssh root@192.168.32.253 /etc/init.d/S55klipper_service restart
