# should be run with -fv option, i.e.
# lsrun -fv group-test.ls

hue 180 saturation 90 brightness 50 kelvin 2700
set group "Pole"

time 5 duration 1.5
off group "Pole"
on group "Pole"

hue 360 saturation 20 brightness 40
set location "Home"
off location "Home"
on location "Home" 
