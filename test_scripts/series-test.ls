# should be run with -fv option, i.e.
# lsrun -fv series-test.ls

units raw

hue 1 saturation 2 brightness 3 kelvin 4 duration 5
set "Middle"

hue series 1000 100
saturation 6
brightness series 2000 200
set "Middle" and "Top"

set "Strip" zone 1 5
set "Middle"
set "Top"
