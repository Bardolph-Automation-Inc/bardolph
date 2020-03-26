time 0 duration 2 on all

duration 120
hue 30 saturation 75 brightness 65 set all

time 120

repeat 10 with next_hue cycle 120
begin
    hue next_hue
    set all
end
