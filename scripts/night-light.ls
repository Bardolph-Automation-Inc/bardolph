brightness 0.01

saturation 80 kelvin 2700
time 0 duration 600
switch_all 0
time 600 duration 600

repeat
    repeat 10 with the_hue cycle
    begin
        hue the_hue
        set all
    end
