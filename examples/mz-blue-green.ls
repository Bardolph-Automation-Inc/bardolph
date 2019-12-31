#
# First show 2/3 blue and 1/3 green. After a delay, it reverses
# reversed blue the green sections.
#
# This script is designed to run in an infinite loop and have a seamless
# transition between cycles. It requires a multi-zone capable light.
#

# Replace "Strip" below with the name of your own multi-zone light.
#
define light "Strip"

kelvin 2700


define green 115
define blue 240

define color_time 15
define color_duration 6
define color_saturation 95
define color_brightness 40

duration color_duration
hue blue
saturation color_saturation
brightness color_brightness 
set light zone 0 5
time 0
hue green set light zone 6 10
hue blue set light zone 11 15
time color_time 

duration color_duration 
hue green
saturation color_saturation  
brightness color_brightness 
set light zone 0 5
time 0
hue blue set light zone 6 10
hue green set light zone 11 15
time color_time 

wait
