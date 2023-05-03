#!/usr/bin/sudo /usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import time
import sys
import logging

# setup logger
log_handler = logging.StreamHandler(stream=sys.stdout)
log_handler.setFormatter(logging.Formatter(fmt="%(asctime)s:%(levelname)s: %(message)s",
                                           datefmt="%H:%M:%S"))
log_handler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# default values and arguments parsing
parser = argparse.ArgumentParser(prog='Orange Pi Zero 2 fan control')
parser.add_argument('pwn_number',
                    default='3',
                    type=int,
                    choices=[1, 2, 3, 4],
                    metavar="PWM_NUMBER",
                    help="Default %(default)s. One of 4 PWM. See orange pi zero 2 user manual.")
parser.add_argument('-i', '--init_power',
                    default='0',
                    type=int,
                    choices=range(0, 101),
                    metavar="PERCENT",
                    help="Default %(default)s %%. Initial fan power [%%].")
parser.add_argument('-f', '--pwm_freq',
                    default='1000',
                    type=int,
                    help="Default %(default)s Hz. PWM frequency [Hz].")
parser.add_argument('-t', '--pwm_threshold',
                    default='380',
                    type=int,
                    help="Default %(default)s Hz. Minimal frequency [Hz] when fan start to rotate.")
parser.add_argument('--min_temp',
                    default='45',
                    type=int,
                    metavar="MIN_TEMP",
                    choices=range(0, 100),
                    help="Default %(default)s °C. Below this temp [°C] fan is off.")
parser.add_argument('--max_temp',
                    default='60',
                    type=int,
                    metavar="MAX_TEMP",
                    choices=range(0, 100),
                    help="Default %(default)s °C. Above this temp [°C] fan is 100 %% power.")
parser.add_argument('--cycle_time',
                    default='5',
                    type=int,
                    metavar="CYCLE_TIME",
                    choices=range(1, 300),
                    help="Default %(default)s s. How often [sec] temperature is measured and fan power is changed.")
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help="Enable verbose mode.")

args = parser.parse_args()

if args.verbose:
    logger.addHandler(log_handler)

PWM_NUMBER = args.pwn_number
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

def set_fan_power(power_percent: float) -> None:
    logger.info(f"GET FAN power = {power_percent: .2f} %")
    if power_percent >= 100:
        pwm_duty_cycle = PWM_FREQ
    elif power_percent <= 0:
        pwm_duty_cycle = 0
    else:
        pwm_duty_cycle = int((power_percent / 100) * (PWM_FREQ - PWM_FREQ_THRESHOLD)
                              + PWM_FREQ_THRESHOLD)
    logger.info(f"SET PWM duty cycle = {pwm_duty_cycle} Hz")
    with open(f"/sys/class/pwm/pwmchip0/pwm{PWM_NUMBER}/duty_cycle", "w+") as dcf:
            dcf.write(str(pwm_duty_cycle))
    logger.info(f"PWM duty cycle is setted to {pwm_duty_cycle} Hz")
    
def process_fan_power(cpu_temp: float) -> float:
    if cpu_temp >= MAX_CPU_TEMP:
        return 100
    elif cpu_temp <= MIN_CPU_TEMP:
        return 0
    return ((cpu_temp - MIN_CPU_TEMP) / (MAX_CPU_TEMP - MIN_CPU_TEMP)) * 100

def pwm_turn_on() -> None:
    logger.info(f"PWM {PWM_NUMBER} is turning on...")
    
    with open(f"/sys/class/pwm/pwmchip0/pwm{PWM_NUMBER}/period", "w+") as period_f:
        period_f.write(str(PWM_FREQ))
    logger.info(f"PWM frequency is setted to {PWM_FREQ} Hz.")

    set_fan_power(INITIAL_FAN_POWER)

    with open(f"/sys/class/pwm/pwmchip0/pwm{PWM_NUMBER}/enable", "w+") as enable_f:
        enable_f.write("1")
    logger.info("PWM turned on.")

def pwm_turn_off() -> None:
    with open(f"/sys/class/pwm/pwmchip0/pwm{PWM_NUMBER}/enable", "w+") as enable_f:
        enable_f.write("0")
    logger.info(f"PWM {PWM_NUMBER} turned off.")

def get_cpu_max_temp() -> float:
    cpu_temp = [0]*4
    for i in range(0, 4):
        with open(f"/sys/class/thermal/thermal_zone{i}/temp", "r") as temp_f:
            cpu_temp[i] = int(temp_f.readline())
    logger.info(f"GET CPU raw temp: {cpu_temp}")
    return max(cpu_temp) / 1000

if __name__ == '__main__':
    try:
        temp_step = (MAX_CPU_TEMP - MIN_CPU_TEMP) / 100
        pwm_turn_on()

        while True:
            cpu_temp = get_cpu_max_temp()
            logger.info(f"GET CPU max temperature = {cpu_temp: .2f} °C")
            fan_power_percent = process_fan_power(cpu_temp)
            set_fan_power(fan_power_percent)
            time.sleep(MEASUREMENT_FREQ)
            logger.info('='*50)
    except KeyboardInterrupt:
        ...
    finally:
        pwm_turn_off()
        logger.info("Exit...")
