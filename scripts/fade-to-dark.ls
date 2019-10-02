# Slowly dims the lights, gradually gives them the color of candlelight,
# and eventually turns them off. Occurs over the period of one hour.

define minutes_20 1200000

time 0 
duration minutes_20
hue 30 saturation 15 brightness 66 kelvin 3000 set all

time minutes_20
saturation 50 brightness 33 kelvin 2500 set all
saturation 75 brightness 0 set all

time 0 duration 3000 off all
