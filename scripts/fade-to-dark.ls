# Slowly dims the lights, gradually gives them the color of candlelight,
# and eventually turns them off. Occurs over the period of one hour.

define delay_20 1200000
define duration_20 1190000

time 0 
duration duration_20
hue 5600 saturation 10000 brightness 36000 kelvin 3000 set all

time delay_20
hue 5450 saturation 30000 brightness 18000 kelvin 2000 set all
hue 5300 saturation 50000 brightness 0 kelvin 1000  set all

time 0 duration 3000 off all
