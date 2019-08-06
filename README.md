# Bardolph
Al Fontes - [bardolph@fontes.org](mailto:bardolph@fontes.org)

**Bardolph** is a facility for controlling [LIFX](https://www.lifx.com/) lights
through a simple scripting language. It is targeted at people who would like
to control or experiment with their lights in an automated way, but who do not 
want to learn a programming language or API.

My intention was also to make the code usable in other Python programs. A 
goal for the parser and virtual machine is to make them accessible through 
reasonably simple entry points.

The program does not use the Internet to
access the bulbs, and no login is required; all of its  communication occurs
over the local WiFi network. You can edit scripts with a basic text editor and
run them from command line.

This project relies heavily on the [lifxlan](https://github.com/mclarkk/lifxlan)
Python library to access the bulbs. You need to have it installed for the code
in this project to run.

The language is missing quite a lot of what you might expect, as it's still
under development. However, it is also very simple, and should be usable
by non-programmers.

## Lightbulb Scripts
A script is a plain-text file in which all whitespace is equivalent. You can 
format it with tabs or put the entire script on a single line if you want. 
Comments begin with the '#' character and continue to the end of the line. All
keywords are in lower-case text. Script file names have a ".ls" extension, 
meaning "lightbulb script".

### Basics
To set the color of one or more lights, the virtual machine will send
four parameters (hue, saturation, brightness, and kelvin) to the bulbs.

Here's an example:
```
# comment
hue 1200 # red
saturation 65500
brightness 40000
kelvin 2700
set all
on all
``` 
This script sets the colors of all known lights , and turns all of them on. The 
meaning of the numerical values, and how the lights process them, is defined
by the LIFX [LAN Protocol](https://lan.developer.lifx.com).

Any values never specified default to zero, or an empty string. This can lead
to unwanted results, so each of the values should be set at least once before
setting the color of any lights.

When a value isn't specified a second time, the previous one gets used again. 
For example, the following uses the same numbers for saturation, brightness,
and kelvin throughout:
```
hue 20000 saturation 65500 brightness 45000 kelvin 2700 set all
hue 40000 set all
```
This script will:
1. Set all lights to HSBK of 20000, 65500, 45000, 2700
1. Set all lights to HSBK of 40000, 65500, 45000, 2700

### Individual Lights
Scripts can control individual lights by name. For example, if you have a light
named "Table", you can set its color with:
```
hue 20000 saturation 65500 brightness 45000 kelvin 2700
set "Table"
```
Light names must be in quotation marks. They can contain spaces, but they may
not contain a linefeed. For example:
```
# Ok
on "Chair Side"

# Error
on "Chair
Side"
```
If a script mentions a name for a light that has not been found or is otherwise
unavailable, an error is sent to the log, and execution of the script
continues. 

### Power Command
The commands to turn the lights on or off resemble the one for colors:
```
off all
on "Table"
```
This turns off all the lights, and turns on the one named "Table".

The "on" and "off" commands have no effect on the color of the lights.
When "on" executes, each light will have whatever its color was when 
it was turned off. If a lights is already on or off, an otherwise 
redundant power operation will have no effect, although it will be sent
to the bulbs.

### Timing Color Changes
Scripts can contain time delays and durations, both of which are are expressed 
in milliseconds. A time delay designates the amount of time to wait before
transmitting the next command to the lights. The duration value is passed
through to the bulbs, and its interpretation is defined through the LIFX API.

For example:
```
off all time 5000 duration 2000 on all off "Table"
```
This will:
1. Immediately turn off all lights.
1. Wait 5,000 ms.
1. Turn on all the lights, ramping up the power over a period of 2,000 ms.
1. Wait 5,000 ms. again.
1. Turn off the light named "Table", taking 2,000 ms. to dim it down to
darkness. 

As mentioned above, the existing values for `time` and `duration` are used
with each command. In this example, `time` is set only
once, but there will be the same delay between every action.

If you want to set multiple lights at the same time, you can specify them using
`and`:
```
time 1000 on "Table" and "Chair Side"  # Uses "and".
```
This script will:
1. Wait 1000 ms. 
1. Turns both lights on *simultaneously*. 

Contrast this to:
```
time 1000 on "Table" on "Chair Side"   # Does not use "and".
```
This script will:
1. Wait 1,000 ms. 
1. Turn on the light named "Table".
1. Wait 1,000 ms.
1. Turn on the light named "Chair Side". 

The `and` keyword works with `set`, `on`, and `off`. When multiple lights are
specified this way, the interpreter attempts to change all of the lights at 
once, with (theoretically) no delay between each one.

#### How Time Is Measured
It's important to note that delay time calculations are based on when
the script started. The delay is not calculated based on the completion 
time of the previous instruction.

For example:
```
time 2000
on all
# Do a lot of slow stuff.
off all
```
The "off" instruction will be executed 2 seconds from the time that
the script was started, and the "off" instruction 4 seconds from that start
time.

If part of a script takes a long time to execute, the wait time may elapse
before the virtual machine is ready for the next instruction. In this case, that
instruction gets executed without any timer delay. If delay times are too 
short for the program to keep up, it will simply keep executing
instructions as fast as it can.

### Pause for Keypress
Instead of using timed delays, a script can wait for a key to be pressed. For
example, to simulate a manual traffic light:
```
saturation 65000 brightness 55000
hue 23000 set all
pause hue 9000 set all
pause hue 63800 set all
```
This script will:
1. Set all the lights to green (hue 23,000).
1. Wait for the user to press a key.
1. Set all the lights to yellow (9,000).
1. Wait for a keypress.
1. Turn the lights red (63,800).

A script can contain both pauses and timed delays. After a pause, the delay
timer is reset.

### Groups and Locations
The `set`, `on`, and `off` commands can be applied to groups and locations.
For example, if you have a location called "Living Room", you can set them 
all to the same color with:
```
hue 50000 saturation 45000 brightness 40000 kelvin 2700
set location "Living Room"
```
Continuing the same example, you can also set the color of all the lights in the
"Reading Lights" group with:
```
set group "Reading Lights"
```
### Definitions 
Symbols can be defined to hold a  commonly-used name or number:
```
define blue 45000 define deep 65530 define dim 12000 
define gradual 4000
define ceiling "Ceiling Light in the Living Room"
hue blue saturation deep brightness dim duration gradual
set ceiling
```
Definitions may refer to other existing symbols:
```
define blue 45000
define b blue
```
### Retrieving Current Colors
The `get` command retrieves  the current settings from a bulb:
```
get "Table Lamp"
hue 20000
set all
```
This script retrieves the values of  `hue`, `saturation`, `brightness`,
and `kelvin`  from the bulb named "Table Lamp". It then
overrides only  `hue`. The `set` command then sets all the lights to
the resulting color.

You can retrieve the colors of all the lights, or the members of a group
or location. In this case, each setting is the arithmetic mean across all the
lights. For example:
```
get group "Reading Lights"
```
This gets the average hue from all of the lights in this group, and that becomes
the hue used in any subsequent `set` action. The same calculation is done on
saturation, brightness, and kelvin, as well.

## Running Scripts
To run a script from the command line:
```
run name.ls
``` 
In this context, "name" contains the name a script. This is equivalent to:
```
python -m controller.run name.ls
```
You can sequentially run multiple scripts. If you specify more than one on the
command line, it will cue them in that order and execute them sequentially.
For example, 
```
run light.ls dark.ls
``` 
would run `light.ls`, and upon its completion, execute `dark.ls`.

### Options
Command-line flags can modify how a script is run. For example:
```
run --verbose test.ls

run -r color_cycle.ls
```
The available options are:
1. -r or --repeat: Repeat the scripts indefinitely, until Ctrl-C is pressed.
1. -v or --verbose: Generate full debugging output while running.
1. -f or --fake: Don't operate on real lights. Instead, use "fake" lights that
just send output to stdout. This can be helpful for debugging and testing.

With the -f option, there will be 5 fake lights, and their name are fixed as
"Table", "Top", "Middle", "Bottom", and "Chair". Two fake groups are
available: "Pole" and "Table". One location named "Home" contains all
of the fake lights, as well.

## Other Programs
Some utility Python programs are available to be run from the command line.
There is a small script for each one of them that runs on any platform
capable of executing a bash script, typically MacOS and Linux systems. All of
these must be run from the directory where Bardolph is installed.

### lsc - Lightbulb Script Compiler
This is equivalent to `python -m controller.lsc`. The syntax is
`lsc name.ls`. Only one file name may be provided.

The acronym LSC stands for "lightbulb script compiler". This meta-compiler
generates a Python file that contains a parsed and encoded version of the
script, in a file called  `__generated__.py`. The generated file can be run 
from the command line like any other Python module for example:
```
lsc scripts/evening.ls
python -m __generated__
```
The generated Python module still relies on the Bardolph runtime code, and
needs to be executed from the same directory.

If you want to use this module in your own Python code, you can import the
and call the function `run_script()`. However, because the module is not 
completely self-contained, ther Bardolph `lib` and `controller` modules
will need to be importable at runtime.

The generated program has two options:
1. `-f` or `--fakes`: Instead of accessing the lights, use "fake" lights that
just send output to the log.
2. `-d` or `--debug`: Use debug-level logging.

For example, after you've generated the python program:
```
python -m __generated__ -fd
```
This would not affect any physical lights, but would send text to the screen
indicating what the script would do.

### snapshot
The `snapshot` command is a bash script wihch is equivalent to
`python -m controller.snapshot`.

This program captures the current state of the lights and generates the
requested type of output. The default output is a human-readable listing
of the lights.

The nature of that output is determined by command-line options. These are 
the most interesting:
1. `-s`: outputs a light script to stdout. If you save that output to a file
and run it as a script, it will restore the lights to the same state,
including color and power.
1. `-t`: outputs text to stdout, in a human-friendly listing of all the known
bulbs, groups, and locations.
1. `-p`: builds file `__generated__.py` based on the current state of
the known bulbs. The resulting file is very similar to the output generated
by the `lsc` command, and can be run with `python -m __generated__`.

## System Requirements
The program has been tested on Python versions 3.5.1 and 3.7.3. I haven't tried
it, but I'm almost certain that it won't run on any 2.x version.

I haven't done any stress testing, so I don't know what the limits are on
script size. Note that the application loads the entire script into memory
beore executing it.

I've run the program on MacOS 10.14.5, Debian Linux Stretch, and the
June, 2019, release of Raspbian. It works fine for me on a Raspberry Pi Zero W.

# Web Server
There is also a very thin web server application that is available. This server
takes a different approach in that the server runs in your home. The advantage
is that you can access this server from your phone, TV, or laptop, as long as
you're on the home WiFi. The disadvantage is you can't access your living room
lights from the office.

The support for the web UI has a lot of non-Python files, and is therefore
available through (https://github.com/al-fontes-jr/bardolph).

## Missing Features
These are among the missing features that I'll be working on, roughly with
this priority:
1. Flow of control, such as loops, branching, and subroutines.
1. Mathematical expressions.
1. Support for devices that aren't bulbs.

## Project Name Source
[Bardolph](https://en.wikipedia.org/wiki/Bardolph_(Shakespeare_character)) was
known for his bulbous nose.
