hue 120 saturation 80 brightness 0.1 kelvin 2700
time 600 duration 600

repeat
    repeat 10 with the_hue cycle 120 begin
        hue the_hue
        set all
    end
