#
# Cycles the three lights on a vertical pole lamp. The lights are named
# "Top", "Middle", and "Bottom". You can use this script if you change the
# defines.
#
# Because the hues maintain a mathematical relationship, the three lights
# always have a pleasing combination.
#
# Note that time and duration are two minutes. This means that the entire cycle
# takes 20 minutes. The bulbs never stop changing, but they do so very
# slowly. For me, this has been a good script for accent/fill lighting in a
# corner.
#

units raw

# Change the name in quotes to the names of your lights.
#
define top "Top"
define middle "Middle"
define bottom "Bottom"

define delay 120000
define dur 120000

define h0 6000
define h1 12000
define h2 18000
define h3 24000
define h4 30000
define h5 36000
define h6 42000
define h7 48000
define h8 54000
define h9 60000
define h10 65535

time 0 duration 3000 saturation 55000 brightness 30000
hue h0 set top
hue h1 set middle
hue h2 set bottom

duration dur

hue h1 set top time 0
hue h2 set middle
hue h3 set bottom

time delay
hue h2 set top time 0
hue h3 set middle
hue h4 set bottom

time delay
hue h3 set top time 0
hue h4 set middle
hue h5 set bottom

time delay
hue h4 set top time 0
hue h5 set middle
hue h6 set bottom

time delay
hue h5 set top time 0
hue h6 set middle
hue h7 set bottom

time delay
hue h6 set top time 0
hue h7 set middle
hue h8 set bottom

time delay
hue h7 set top time 0
hue h8 set middle
hue h9 set bottom

time delay
hue h8 set top time 0
hue h9 set middle
hue h10 set bottom

time delay
hue h9 set top time 0
hue h10 set middle
hue h0 set bottom

time delay
hue h10 set top time 0
hue h0 set middle
hue h1 set bottom

time delay
hue h0 set top time 0
hue h1 set middle
hue h2 set bottom
