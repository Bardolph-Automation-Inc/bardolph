units raw
brightness 5
units logical

saturation 80 kelvin 2700

define switch_all with the_hue begin
    hue the_hue set all
end

time 0 duration 600
switch_all 0

time 600 duration 600
switch_all 36
switch_all 72
switch_all 108
switch_all 144
switch_all 180
switch_all 216
switch_all 252
switch_all 288
switch_all 324
wait
