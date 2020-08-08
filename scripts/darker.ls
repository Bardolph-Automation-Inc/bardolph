duration 1.5 time 0
repeat all as light begin
    get light
    brightness {brightness * 0.67}
    if {brightness < 1}
        brightness 1
    set light
end
