duration 1.5 time 0
repeat all as light begin
    get light
    brightness {brightness * 1.33}
    if {brightness > 100}
        brightness 100
    set light
end
