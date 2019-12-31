# Displays a different color in each zone across the spectrum.
#

define light "Strip"  # Replace "Strip" here.

time 0 duration 2
saturation 0 brightness 20 kelvin 2500 set light
saturation 80 brightness 80
duration 6 time 4
hue 0 set light zone 0 time 0
hue 22 set light zone 1
hue 45 set light zone 2
hue 68 set light zone 3
hue 90 set light zone 4
hue 112 set light zone 5
hue 135 set light zone 6
hue 158 set light zone 7
hue 180 set light zone 8
hue 202 set light zone 9
hue 225 set light zone 10
hue 248 set light zone 11
hue 270 set light zone 12
hue 292 set light zone 13
hue 315 set light zone 14
hue 338 set light zone 15
wait
