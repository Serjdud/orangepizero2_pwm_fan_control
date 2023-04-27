#!/bin/bash

if [[ "$1" > 4 ]] || [[ "$1" < 1 ]]; then
  echo "First argument is PWM number. It must be from 1 to 4."
  exit
fi

path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$path"

sudo chmod o+rw /sys/class/pwm/pwmchip0/export
if [ ! -d "/sys/class/pwm/pwmchip0/pwm${1}" ]; then
  echo $1 > /sys/class/pwm/pwmchip0/export
fi

sudo chmod o+rw /sys/class/pwm/pwmchip0/pwm*/period
sudo chmod o+rw /sys/class/pwm/pwmchip0/pwm*/duty_cycle
sudo chmod o+rw /sys/class/pwm/pwmchip0/pwm*/enable
sudo chmod o+r /sys/class/thermal/thermal_zone*/temp

sudo chmod +x ./fan_control.py
sudo python3 ./fan_control.py "$@"
