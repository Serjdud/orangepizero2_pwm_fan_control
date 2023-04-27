#!/bin/bash
path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$path"

sudo chmod o+rw /sys/class/pwm/pwmchip0/export
sudo chmod o+rw /sys/class/pwm/pwmchip0/pwm*/period
sudo chmod o+rw /sys/class/pwm/pwmchip0/pwm*/duty_cycle
sudo chmod o+rw /sys/class/pwm/pwmchip0/pwm*/enable
sudo chmod o+r /sys/class/thermal/thermal_zone*/temp

sudo chmod +x ./fan_control.py
sudo python3 ./fan_control.py "$@"
