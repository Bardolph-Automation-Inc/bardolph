begin                              
  on "Top" and "Middle"
  on "Bottom" and "Table"
  
  hue 23483 saturation 65535 brightness 54170 kelvin 2700
  time 1000 duration 0
  set "Top"
  
  hue 0
  time 500
  saturation 65535
  brightness 54170
  kelvin 2700
  time 1000
  duration 0
  set "Bottom" and "Top"
  
  off "Bottom"
  pause
  
  hue 42779
  saturation 63568
  brightness 36145
  kelvin 2700
  set "Middle"
  
  hue 33495
  saturation 65535
  brightness 46573
  kelvin 2700
  set "Bottom"
  
  hue 42961
  saturation 0
  brightness 41478
  kelvin 2700
  set "Table"
end
