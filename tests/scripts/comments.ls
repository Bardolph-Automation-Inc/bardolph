begin                              
  on "Top"
  on "Middle"
  on "Bottom"
  on "Table"
  
#comment 1

  define x 12345
  define n "A Name"

  hue 42779 # comment 2
  saturation 63568
  brightness 36145
  kelvin 2700
  set "Middle"
  
  # comment 3
  # comment 4
  hue 33495
  saturation 65535
  brightness 46573
  kelvin 2700
  set "Bottom"
  
  hue x
  saturation 0
  brightness 41478
  kelvin 2700
  set "Table" and n
end
