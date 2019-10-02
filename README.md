![bulb](web/static/colorBulb-192.png) 
# Bardolph 
Al Fontes - [bardolph@fontes.org](mailto:bardolph@fontes.org)

## Introduction
**Bardolph** is a facility for controlling [LIFX](https://www.lifx.com/) lights
through a simple scripting language. It is targeted at people who would like
to control or experiment with their lights in an automated way, but who do not 
want to learn a programming language or API.

The program does not use the Internet to access the bulbs, and no login is 
required; all of its  communication occurs over the local WiFi network. You 
can edit scripts with a basic text editor and run them from the command line.

This project relies heavily on the [lifxlan](https://pypi.org/project/lifxlan/)
Python library to access the bulbs. You need to have it installed for the code
in this project to run. If you run the web server, you will also need 
[flup](https://www.saddi.com/software/flup) and
[Flask](https://palletsprojects.com/p/flask/).

The language is missing quite a lot of what you might expect, as it's still
under development. However, it is also very simple, and should be usable
by non-programmers.

### Lightbulb Scripts
A script is a plain-text file in which all whitespace is equivalent. You can 
format it with tabs or put the entire script on a single line if you want. 
Comments begin with the '#' character and continue to the end of the line. All
keywords are in lower-case text. Script file names have a ".ls" extension, 
meaning "lightbulb script".

#### Quick Examples
The source distribution contains some sample scripts in the `scripts` directory.
They should work with whatever lights may be on the network. For example, to
turn on all your lights:
```
run scripts/all_on.ls
```
That script contains the following code:
```
duration 1500 on all
```
In this case, `run` is a bash shell script that runs the Python `run.py` module.

The `duration` parameter, which is described below, works to slowly shut off the
lights
over a period 1500 ms., which is a much nicer experience than abruptly turning
them off with no dimming.

In another example, to turn all the lights on, wait for 5 minutes, and then turn
them all off:
```
run scripts/on5.ls
```
The code for that script:
```
duration 1500 on all
time 300000 off all
```
The application runs in the foreground as long as a script is running. In this
example, the application will run for 5 minutes. However, it will spend most of
its time inside a `sleep()` call to avoid burdening the CPU. In my experience,
scripts spend most of their time inside a delay, and  execution for the 
application takes up less than 10% of the CPU cycles on a Raspberry Pi Zero.

You can kill the script and quit by pressing Ctrl-C. You may want to run the
program as a background job, which will terminate when the script is done.

### Web Server
The web server component makes scripts available in a user-friendly manner.
It implements a simple web page that lists available scripts and provides a
1:1 mapping betwen scripts and URL's. The server is designed to run locally, 
on your WiFi network.

For example, if have a machine with the hostname
 `myserver.local`, you could launch the  `all_on.ls` script by going to
 `http://myserver.local/all-on` with any browser on your WiFi network.
 Because scripts can run over a long period of time, even indefinitely, 
 a cheap, dedicated device like a Raspberry Pi is an ideal way to host the 
 web server.

This is currently an experimental feature, as getting it to run can be a bit of a chore.
I describe the process for setting up and running a server in
[docs/web_server.md](docs/web_server.md).

## Python API
I've attempted to make it easy to use Bardolph scripts in your Python code.
For some uses, this may be significantly easier than learning and using a
full-purpose Python library. For example, here's a complete program that
turns all the lights off and then on again:
```
from bardolph.controller import ls_module

script = "time 5000 duration 1500 off all on all"
ls_module.configure()
ls_module.queue_script(script)
```
More information on using scripts in Python code is available in
[docs/python_api.md](docs/python_api.md)

## Script Basics
Internally, launching a script is a two-step process. First, a parser reads the
source file and compiles it into a sequence of encoded instructions. Next, a
simple virtual machine executes those instructions. A job-control facility
maintains a queue, allowing execution of a sequence of compiled scripts.

You set the color and brightness of the lights specifying
4 numbers: hue, saturation, brightness, and kelvin. The value
for hue is considered to be an angle, expressed in degrees.
The values for saturation and brightness are treated as percentages,
while kelvin the temperature modification applied to the resulting color.
All of these number must be positive, and may be floating-point
values. Percentages above 100 are considered invalid, as are
kelvin values less than 2,500 or greater than 9,000.

The easiest way to understand the meaning of these numbers is to
use the LIFX mobile app and observe the displayed numbers as
you change the lighting.

Your script supplies these parameters, and the Bardolph virtual machine 
sends them to the bulbs.

Here's another example, including some comments:
```
# comment
hue 360 # red
saturation 100
brightness 60
kelvin 2700
set all
on all
``` 
This script sets the colors of all known lights to a bright shade of red and 
turns all of them on. 

When a value isn't specified a second time, the VM uses the existing value. 
For example, the following reuses numbers for saturation, brightness,
and kelvin throughout:
```
hue 120 saturation 100 brightness 50 kelvin 2700 set all
hue 180 set all
```
This script will:
1. Set all lights to HSBK of 120, 100, 50, 2700
1. Set all lights to HSBK of 180, 100, 50, 2700

Any uninitialized values default to zero, or an empty string. This can lead
to unwanted results, so each of the values should be set at least once before
setting the color of any lights. Or, consider starting your script with
`get all` (the `get` command is described below).

If you prefer to send unmodified numbers to the bulbs, as specified by the 
[LIFX API](https://lan.developer.lifx.com), you can use "raw" units (and switch
back to "logical" units if desired):
```
units raw
hue 30000 saturation 65535 brightness 32767 kelvin 2700 set all
units logical
hue 165 saturation 100 brightness 50 kelvin 2700 set all
```
### Individual Lights
Scripts can control individual lights by name. For example, if you have a light
named "Table", you can set its color with:
```
hue 120 saturation 100 brightness 75 kelvin 2700
set "Table"
```
A light's name is configured when you do initial setup with the LIFX software.

When they appear in a script, bulb names must be in quotation marks. They 
can  contain spaces, but  may not contain a linefeed. For example:
```
# Ok
on "Chair Side"

# Error
on "Chair
Side"
```
If a script contains a name for a light that has not been discovered or is 
otherwise unavailable, an error is sent to the log, but execution of the script
continues. 

### Power Command
The commands to turn the lights on or off resemble the `set` command:
```
off all
on "Table"
```
This turns off all the lights, and turns on the one named "Table".

The "on" and "off" commands have no effect on the color of the lights.
When "on" executes, each light will have whatever its color was when 
it was turned off. If a lights is already on or off, an otherwise 
redundant power operation will have no effect, although the VM does send it
to the bulbs.

### Timing Color Changes
Scripts can contain time delays and durations, both of which are are expressed 
in milliseconds. A time delay designates the amount of time to wait before
transmitting the next command to the lights. The duration value is passed
through to the bulbs, and its interpretation is defined through the 
 [LIFX API](https://lan.developer.lifx.com).
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

This contrasts with:
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
saturation 100 brightness 80
hue 120 set all
pause hue 50 set all
pause hue 360 set all
```
This script will:
1. Set all the lights to green (hue 120).
1. Wait for the user to press a key.
1. Set all the lights to yellow (50).
1. Wait for a keypress.
1. Turn the lights red (360).

A script can contain both pauses and timed delays. After a pause, the delay
timer is reset.

### Groups and Locations
The `set`, `on`, and `off` commands can be applied to groups and locations.
For example, if you have a location called "Living Room", you can set them 
all to the same color with:
```
hue 50000 saturation 80 brightness 75 kelvin 2700
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
define blue 250 define deep 100 define dim 20 
define gradual 4000
define ceiling "Ceiling Light in the Living Room"
hue blue saturation deep brightness dim duration gradual
set ceiling
```
Definitions may refer to other existing symbols:
```
define blue 250
define b blue
```
### Retrieving Current Colors
The `get` command retrieves  the current settings from a bulb:
```
get "Table Lamp"
hue 20
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

To retrieve the average valuess  from all known lights and use them in subsequent
commands:
```
get all
```
## Running Scripts
Run a script from the command line:
```
run name.ls
``` 
In this context, "name" contains the name of a script. This is equivalent to:
```
python -m bardolph.controller.run name.ls
```
You can queue up multiple scripts. If you specify more than one on the
command line, it will queue them in that order and execute them sequentially:
```
run light.ls dark.ls
``` 
would run `light.ls`, and upon completion, execute `dark.ls`.

### Options
Command-line flags modify how a script is run. For example:
```
run --verbose test.ls

run -r color_cycle.ls
```
Available options:
1. -r or --repeat: Repeat the scripts indefinitely, until Ctrl-C is pressed.
1. -v or --verbose: Generate full debugging output while running.
1. -f or --fake: Don't operate on real lights. Instead, use "fake" lights that
just send output to stdout. This can be helpful for debugging and testing.

With the -f option, there will be 5 fake lights, and their name are fixed as
"Table", "Top", "Middle", "Bottom", and "Chair". Two fake groups are
available: "Pole" and "Table". One location named "Home" contains all
of the fake lights, as well. If you want to use a different set of fake lights,
you will need to edit some Python code. Specificlly, you'll need to modify
`LightSet.discover` in `tests/fake_light_set.py`.

## Other Programs
Some utility Python programs are available to be run from the command line.
A small script for each one of them runs on any platform
capable of executing a bash script, typically MacOS and Linux systems. All of
these must be run from the directory where Bardolph is installed.

### lsc - Lightbulb Script Compiler
This is equivalent to `python -m bardolph.controller.lsc`. The syntax is
`lsc name.ls`. Only one file name may be provided.

LSC stands for "lightbulb script compiler". That meta-compiler writes a 
parsed and encoded version of the script, along with run-time  support, to 
file  `__generated__.py`. The generated file can be run  grom the command
line like any other Python module:
```
lsc scripts/evening.ls
python -m __generated__
```
The generated Python module relies on the Bardolph runtime code.

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
`python -m bardoolph.controller.snapshot`.

This program captures the current state of the lights and generates the
requested type of output. The default output is a human-readable listing
of the lights.

The nature of that output is determined by command-line options, notably:
1. `-s`: outputs a light script to stdout. If you save that output to a file
and run it as a script, it will restore the lights to the same state,
including color and power.
1. `-t`: outputs text to stdout, in a human-friendly listing of all the known
bulbs, groups, and locations.
1. `-p`: builds file `__generated__.py` based on the current state of
the known bulbs. The resulting file is very similar to the output generated
by the `lsc` command, and can be run with `python -m __generated__`.

## System Requirements
The program has been tested on Python version 3.7.3. I haven't tried
it, but I'm almost certain that it won't run on any 2.x version.

Because I haven't done any stress testing, I don't know the limits on
script size. Note that the application loads the encoded script into memory
before executing it.

I've run the program on MacOS 10.14.5, Debian Linux Stretch, and the
June, 2019, release of Raspbian. It works fine for me on a Raspberry Pi Zero W,
controlling 5 bulbs.

## Missing Features
These are among the missing features that I'll be working on, roughly with
this priority:
1. Easy-to-use web server.
1. Flow of control, such as loops, branching, and subroutines.
1. Mathematical expressions.
1. Support for devices that aren't bulbs (I don't own anything but bulbs).

## Project Name Source
[Bardolph](https://en.wikipedia.org/wiki/Bardolph_(Shakespeare_character)) was
known for his bulbous nose.
