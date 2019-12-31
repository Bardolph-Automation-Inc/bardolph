#
# Example script controlling some groups.
#
# Turn on all the lights in location "Home". Set the "Furniture" group to
# one color, and set the group "Pole" to a higher saturation.
#

time 1.5 saturation 80 brightness 80

on location "Home"

hue 120 brightness 80

saturation 50 set group "Furniture"
saturation 80 set group "Pole"
