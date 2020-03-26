duration 2 on all

duration 10 time 10 saturation 75 brightness 60

define hue_set with new_hue
begin
    hue new_hue set all
end

repeat 10 with the_hue from 0 to 360
begin
    hue_set the_hue
end
