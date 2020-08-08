time 0 duration 300 saturation 90 brightness 5 kelvin 2700

repeat begin
    time 0
    repeat all as light with _hue cycle 30 begin
        hue _hue set light
    end
    time 10
    wait
end