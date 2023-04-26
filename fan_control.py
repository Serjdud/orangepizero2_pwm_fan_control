#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import time
import sys

# default values and arguments parsing
parser = argparse.ArgumentParser(prog='Orange Pi Zero 2 fan control')
parser.add_argument('-n', '--pwm_num',
                    default='3',
                    type=int,
                    choices=[1, 2, 3, 4],
                    help="One of 4 PWM. See orange pi zero 2 user manual")
parser.add_argument('-p', '--init_power',
                    default='0',
                    type=int,
                    choices=range(0, 101),
                    help="Initial fan power in percent")
parser.add_argument('-f', '--pwm_freq',
                    default='1000',
                    type=int,
                    help="PWM frequency")
parser.add_argument('-t', '--pwm_threshold',
                    default='350',
                    type=int,
                    help="Minimal frequency when fan start to rotate")
parser.add_argument('--min_temp',
                    default='40',
                    type=int,
                    choices=range(0, 100),
                    help="Below this temp fan is off")
parser.add_argument('--max_temp',
                    default='60',
                    type=int,
                    choices=range(0, 100),
                    help="Above this temp fan is 100% power")
parser.add_argument('--cycle_time',
                    default='10',
                    type=int,
                    choices=range(0.1, 300),
                    help="How often [s] temperature is measured and fan_control change fan power")

args = parser.parse_args()
PWM_NUMBER = args.pwm_num
PWM_FREQ = args.pwm_freq
PWM_FREQ_THRESHOLD = args.pwm_threshold
INITIAL_FAN_POWER = args.init_power
MIN_CPU_TEMP = args.min_temp
MAX_CPU_TEMP = args.max_temp
MEASUREMENT_FREQ = args.cycle_time

# checks values
if MAX_CPU_TEMP <= MIN_CPU_TEMP:
    raise Exception(" Maximum CPU temp must be < minimum cpu temp")
if PWM_FREQ_THRESHOLD >= PWM_FREQ:
    raise Exception("PWM frequency threshold must be <= pwm frequency")

def set_fan_power(power_percent: int) -> None:
    if power_percent >= 100:
        pwm_duty_cycle = PWM_FREQ
    elif power_percent <= 0:
        pwm_duty_cycle = 0
    else:
        pwm_duty_cycle = ((power_percent / 100) * (PWM_FREQ - PWM_FREQ_THRESHOLD)
                              + PWM_FREQ_THRESHOLD)
    with open(f"/sys/class/pwm/pwmchip0/pwm{PWM_NUMBER}/duty_cycle", "w+") as dcf:
            dcf.write(str(pwm_duty_cycle))

def pwm_turn_on() -> None:
    with open("/sys/class/pwm/pwmchip0/export", "w+") as export_f:
        export_f.write(str(PWM_NUMBER))
    with open(f"/sys/class/pwm/pwmchip0/pwm{PWM_NUMBER}/period", "w+") as period_f:
        period_f.write(str(PWM_FREQ))
    set_fan_power(INITIAL_FAN_POWER)
    with open(f"/sys/class/pwm/pwmchip0/pwm{PWM_NUMBER}/enable", "w+") as enable_f:
        enable_f.write("1")

def pwm_turn_off() -> None:
    set_fan_power(0)
    with open(f"/sys/class/pwm/pwmchip0/pwm{PWM_NUMBER}/enable", "w+") as enable_f:
        enable_f.write("0")

def get_cpu_max_temp() -> int:
    cpu_temp = []
    for i in range(0, 4):
        with open(f"/sys/class/thermal/thermal_zone{i}/temp", "r") as temp_f:
            cpu_temp[i] = int(temp_f.readline())
    return max(cpu_temp) / 1000

if __name__ == 'fan_control.py':
    try:
        temp_step = (MAX_CPU_TEMP - MIN_CPU_TEMP) / 100
        pwm_turn_on()

        while True:
            cpu_temp = get_cpu_max_temp()

            if cpu_temp >= MAX_CPU_TEMP:
                fan_power_percent = 100
            elif cpu_temp <= MIN_CPU_TEMP:
                fan_power_percent = 0
            else:
                fan_power_percent = ((cpu_temp - MIN_CPU_TEMP) / (MAX_CPU_TEMP - MIN_CPU_TEMP)) * 100
            
            set_fan_power(fan_power_percent)
            time.sleep(MEASUREMENT_FREQ)
    
    except KeyboardInterrupt:
        pwm_turn_off()
        sys.exit()
