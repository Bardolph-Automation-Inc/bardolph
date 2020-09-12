assign delay {3 * 60}
duration delay
saturation 90
brightness 0.5
kelvin 2700

repeat
    repeat 20 with _base_hue cycle begin
        repeat all as light with _hue from _base_hue to {_base_hue + 60}
        begin
            hue _hue set light
            time 0
        end
        time delay
        duration delay
    end
