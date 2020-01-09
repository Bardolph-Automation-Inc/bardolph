.. figure:: logo.png
   :align: center
   
   http://www.bardolph.org

.. index::
   single: language reference
   
.. _language:

Lightbulb Script Reference
##########################
This page describes the syntax and capabilities of Bardolph's scripting
language. For information on how to run a script, please see
:ref:`command_line`.

Internally, launching a script is a two-step process. First, a parser reads the
source file and compiles it into a sequence of encoded instructions. Next, a
simple virtual machine executes those instructions. A job-control facility
maintains a queue, allowing execution of a sequence of compiled scripts.

A script sets the color and brightness of the lights by specifying
5 numbers: `hue`, `saturation`, `brightness`, `kelvin`, and `duration`.
During execution, the Bardolph virtual machine sends these parameters
to the lights.

The easiest way to understand the meaning of these numbers is to use 
the LIFX mobile app and observe the displayed numbers as you change
the lighting.

The value you supply for `hue` is an angle expressed in
in degrees, normally between 0 and 360. The values for `saturation` 
and `brightness` are treated as percentages, while `kelvin` is a 
temperature modification applied by the bulbs to the resulting color.

All of these number must be positive, and may be floating-point
values. Percentages above 100 are considered invalid. Angles
greater than or equal to 360 are normalized to a number less
than 360 by modulo arithmetic.

.. note:: The term *color* is somewhat ambiguous. Intuitively, you may
  consider brightness (intensity) to be separate from a bulb's color. 
  However, for simplicity here, "color" always refers
  to the tone of the light and its intensity. Therefore,
  in this documentation, "setting the color" of a bulb means that
  you are specifying both the frequency and the brightness of the light that
  the bulb produces.

A script is a plain-text file in which all whitespace is equivalent. You can 
format it with tabs or even put the entire script on a single line. 
Comments begin with the '#' character and continue to the end of the line. All
keywords are in lower-case text. By convention, script file names have the ".ls"
extension, meaning "lightbulb script".

Here's an example, showing some comments::

  # comment
  hue 360 # red
  saturation 100 # 100% saturation
  brightness 60.0 # 60% brightness
  kelvin 2700
  set all
  on all

This script sets the colors of all known lights to a bright shade of red and 
turns all of them on. 

When a value isn't specified a second time, the VM uses the existing value. 
For example, the following reuses numbers for `saturation`, `brightness`,
and `kelvin`::

  hue 120 saturation 100 brightness 50 kelvin 2700 set all
  hue 180 set all

This script will:

#. Set all lights to HSBK of 120, 100, 50, 2700
#. Set all lights to HSBK of 180, 100, 50, 2700

Any uninitialized values default to zero, or an empty string. This can lead
to unwanted results, so each of the values should be set at least once before
setting the color of any lights. Or, consider starting your script with
`get all` (the `get` command is described below).

.. index::
   single: individual lights
  
Individual Lights
=================
Scripts can control individual lights by name. For example, if you have a light
named "Table", you can set its color with::

  hue 120 saturation 100 brightness 75 kelvin 2700
  set "Table"

A light's name is configured when you do initial setup with the LIFX software.

When they appear in a script, bulb names must be in quotation marks. They 
can  contain spaces, but  may not contain a linefeed. For example::

  # Ok
  on "Chair Side"
  
  # Error
  on "Chair
  Side"

If a script contains a name for a light that has not been discovered or is 
otherwise unavailable, an error is sent to the log, but execution of the script
continues. 

.. index::
   single: multi-zone

Multi-Zone Lights
=================
With multiple-zone lights, the `set` command works the same, 
but you can limit which zones it affects. It can set all of 
them to the same color, set the color of a single zone, or set
it for a range of them. For example, I have a Z LED strip, which
I named "Strip". I can set the entire device to one color with::

  hue 150 saturation 100 brightness 50 kelvin 2700 duration 1.5
  set "Strip"
  
To set only one zone, add a `zone` clause with a single number::

  set "Strip" zone 5
  
To set multiple zones, specify a range with starting and ending
zone numbers::

  set "Strip" zone 0 8

Note that the zone numbers start with zero. If you try use a zone on
a light that doesn't have that capability, an error will be sent to
the log, and the light will not be accessed. Unlike Python ranges, the
numbers are inclusive. For example, `zone 1 3` would include zones 1, 2,
and 3.

.. index::
   single: power

Power Command
=============
The commands to turn the lights on or off resemble the `set` command::

  off all
  on "Table"

This turns off all the lights, and turns on the one named "Table".

The "on" and "off" commands have no effect on the color of the lights.
When "on" executes, each light will have whatever its color was when 
it was turned off. If a light is already on or off, an otherwise 
redundant power operation will have no visible effect, although the
VM does send the power command to the bulbs.

When applied to a multi-zone light, the entire device is powered
on or off; you can't set the power for individual zones (although you
can set the brightness to zero).

.. index::
   single: abbreviations
 
Abbreviations
=============
Scripts can be much terser with shorthand parameter names: `h` (hue),
`s` (saturation), `b` (brightness), and `k` (kelvin). The following two
lines do the same thing::

  hue 180 saturation 100 brightness 50 kelvin 2700 set all
  h 180 s 100 b 50 k 2700 set all

.. index::
   single: timing
   
Timing Color Changes
====================
Scripts can contain time delays and durations, both of which are are expressed 
in seconds. A time delay designates the amount of time to wait before
transmitting the next command to the lights. The duration value is passed
through to the bulbs, and its interpretation is defined by the 
`LIFX API <https://lan.developer.lifx.com>`_. Basically, by setting a duration,
you determine how long it should take the bulb to transition to its new
state. For example::

  off all time 5 duration 1.5 on all off "Table"

This will:

#. Immediately turn off all lights instantaneously.
#. Wait 5 seconds.
#. Turn on all the lights, but ramp up the brightness over a period of 1.5 seconds.
#. Wait 5 seconds again.
#. Dim down the light named "Table" over a period of 1.5 seconds until it is off. 

The underlying API has a precision down to milliseconds. For example, all digits
are significant in a `time` parameter of `1.234`.

As mentioned above, the existing values for `time` and `duration` are re-used
with each command. In this example, `time` is set only
once, but there will be the same delay between every action.

Multiple Lights Using `and`
---------------------------
If you want to set multiple lights at the same time, you can chain them using
`and`::

  time 2 on "Table" and "Chair Side"  # Uses "and".

This script will:

#. Wait 2 seconds. 
#. Turn both lights on *simultaneously*. 

This contrasts with::

  time 2 on "Table" on "Chair Side"   # Does not use "and".

This script will:

#. Wait 2 seconds. 
#. Turn on the light named "Table".
#. Wait 2 seconds.
#. Turn on the light named "Chair Side". 

The `and` keyword works with `set`, `on`, and `off`. When multiple lights are
specified this way, the interpreter attempts to change all of the lights at 
once, with (theoretically) no delay between each one.

If a script specifies zones, the `and` comes after the zone numbers. This
can be convenient for coordinating a multi-zone light with single-zone
bulbs. For example, with a multi-zone light named "Strip" and a bulb named
"Table"::

  hue 120 saturation 75 brightness 75 kelvin 2700 duration 1.5
  set "Strip" zone 0 5 and "Table"

Here's an example of simultaneously setting multiple zones on the
same light::

  set "Strip" zone 2 and "Strip" zone 13 15

How Time Is Measured
====================
It's important to note that delay time calculations are based on when
the script started. The delay is not calculated based on the completion 
time of the previous instruction.

For example::

  time 2
  on all
  # Do a lot of slow stuff.
  off all

The "off" instruction will be executed 2 seconds from the time that
the script was started, and the "off" instruction 4 seconds from that start
time.

If part of a script takes a long time to execute, the wait time may elapse
before the virtual machine is ready for the next instruction. In this case, that
instruction gets executed without any timer delay. If delay times are too 
short for the program to keep up, it will simply keep executing
instructions as fast as it can.

.. index::
   single: clock time
   single: time of day
   
Wait for Time of Day
=====================
Instead of waiting for a delay to elapse, you can specify the specific time that
an action occurs, using the `at` modifier with the `time` command. For example,
to turn on all the lights at 8:00 a.m.::

  time at 8:00 on all

All times are specified using a 24-hour clock, with midnight at 0:00.

In this context, you can use wildcards to match more than one possible
time. For example, to turn on the lights on the hour and turn them off on the
half-hour::

  time at *:00 on all time at *:30 off all
  
The pattern used to specify the time can replace one or two digits with the
asterisk. Here are some examples of valid patterns:

* `2*:00` - matches 21:00, 22:00, and 23:00.
* `1:*5` - matches 1:05, 1:15, 1:25, 1:35, 1:45 and 1:55.
* `*:30` - matches any half-hour.

These are not valid patterns:

* `*` or `*:*` - matches anything and is therefore meaningless.
* `12:8*` - not a valid time.
* `**:08` - only one asterisk is necessary.
* '12:5` - minutes need to be expressed as two digits.

Note that the language is procedural, not declarative. This means that the
script is executed from top to bottom. For example::

  time at 10:00 on all
  time at 9:00 off all
  
This will turn on all the lights at 10:00 a.m., wait 23 hours, and turn them
off again the next day. If you have a regular set of actions you'd like to
take, you can launch a script in repeat mode and let it run indefinitely.

You can combine patterns to create more complicated behavior. For example, this
will turn on the lights the next time it's either 15 or 45 minutes past the
hour::

  time at *:15 or *:45 on all

This type of script would typically be run in repeat mode.

After a scheduled wait, the delay timer is essentially reset. For example::
  
  time at 12:00 on all
  time 60 off all
  
This would turn on all the lights at noon and then turm them off 60 seconds
later, which would be at 12:01 p.m.

.. index::
   single: pause
   single: keypress

Pause for Keypress
==================
Instead of using timed delays, a script can wait for a key to be pressed. For
example, to simulate a manual traffic light::

  saturation 100 brightness 80
  hue 120 set all
  pause hue 50 set all
  pause hue 360 set all

This script will:

#. Set all the lights to green (hue 120).
#. Wait for the user to press a key.
#. Set all the lights to yellow (50).
#. Wait for a keypress.
#. Turn the lights red (360).

A script can contain both pauses and timed delays. After a pause, the delay
timer is reset. For example::

  time at 12:00 on all
  pause off all
  time 10 on all

This script turns on all the lights at 12:00 noon. It then waits
for the user to press a key at the keyboard. When a key has been pressed,
it turns off all the lights, waits 10 s, and turns them on again.

.. index::
   single: groups
   single: locations
   
Wait With No Action
===================
To wait for the next time interval without doing anything::

  wait

This can be useful to keep a script active until the last command has been
executed. For example::

  time 0 hue 120 saturation 90 brightness 50 kelvin 2700
  duration 200 set all
  time 200 wait
  
In this example, the `set` command will take 200 seconds to fully take effect.
The script adds a 200-second wait to keep it from exiting before that slow `set`
completes. If a script is waiting in the queue, this prevents that next script
from starting before the 200-second duration has elapsed.
   
Groups and Locations
====================
The `set`, `on`, and `off` commands can be applied to groups and locations.
For example, if you have a location called "Living Room", you can turn them
on and set them all to the same color with::

  on location "Living Room"
  hue 120 saturation 80 brightness 75 kelvin 2700
  set location "Living Room"

Continuing the same example, you can also set the color of all the lights in the
"Reading Lights" group with::

  set group "Reading Lights"

You can combine lights, groups, and locations with the `and` keyword::

  set location "Living Room" and "Table" and group "Reading Lights"


.. index::
   single: series

Series of Values
================
When setting the color of multiple lights, you can use a running series of
incremental values. For example::

  hue series 100 10
  saturation 50 brightness 60 kelvin 2700
  set "Top" 
  set "Middle" and "Bottom"

This example assumes that three lights named "Top", "Middle", and
"Bottom" are all available on the network. This script will:

#. Set light "Top" to HSBK of 100, 50, 60, 2700
#. Set light "Middle" to HSBK of 110, 50, 60, 2700
#. Set light "Bottom" to HSBK of 110, 50, 60, 2700

Note that when setting more that one light using `and`, the series
is advanced only once, and the same value is used for all lights
in the `set` command's list.

Series can be used for `hue`, `saturation`, `brightness`, and
`kelvin`. In the case of a group or location, all member lights are
given the same value from the series.

A series advances with each `set` command, regardless of what
it's applied to. For example::

  hue series 100 10

  set "Top" 
  set group "Furniture"

This will set the hue for light "Top" to 100. Every light in the group
"Furniture" will get a hue of 110.

.. index::
   single: range

Range of Values
===============
When setting the color of multiple lights, you can use a range, and each
light will get a different, evenly-distributed value. For example::

  hue range 100 200 3
  saturation 50 brightness 40 kelvin 2700
  set "Top"
  set "Middle"
  set "Bottom"

The parameters to `range` are start, end, and count. In this example, the 
range has a first value of 200, a final value of 300, and will produce
3 evenly-divided numbers. This script will:

#. Set light "Top" to HSBK of 100, 50, 40, 2700
#. Set light "Middle" to HSBK of 150, 50, 40, 2700
#. Set light "Bottom" to HSBK of 200, 50, 40, 2700

The values are assigned to the lights using the same order
in which they appear in the script. Ranges can be used for `hue`,
`saturation`, `brightness`, and `kelvin`.

Note that a range will keep going, even after you use more numbers
than originally specified.

.. index::
   single: define
   single: symbols

Definitions
===========
Symbols can be defined to hold a  commonly-used name or number::

  define blue 240 define deep 100 define dim 20 
  define gradual 4
  define ceiling "Ceiling Light in the Living Room"
  hue blue saturation deep brightness dim duration gradual
  set ceiling

Definitions may refer to other existing symbols::

  define blue 240
  define b blue

.. index::
   single: get
   single: retrieving colors

Retrieving Current Color
========================
The `get` command retrieves the current settings from a single light::

  get "Table Lamp"
  hue 20
  set all

This script retrieves the values of `hue`, `saturation`, `brightness`,
and `kelvin` from the bulb named "Table Lamp". It then
overrides only `hue`. The `set` command then sets all the 
other lights to the resulting color.

From a multi-zone light, you can retrieve the color of a single zone or
the entire device::

  get "Strip" zone 5
  get "Strip"

Note that you cannot get values for locations, groups, multiple zones,
or multiple lights::

  # Errors
  get "Table Lamp" and "Chair Side"
  get all
  
  # Errors
  get location "Living Room"
  get group "Reading Lights"
  
  # Error
  get "Strip" zone 5 6

.. index::
   single: raw units
   single: logical units

Raw and Logical Units
=====================
By default, numerical values in scripts are given in units that should be
convenient to humans. However, during communication with the lights,
those numbers are mapped to unsigned, 16-bit integer values as specified
by the `LIFX API <https://lan.developer.lifx.com>`_.

If you prefer to send unmodified numbers to the bulbs as specified by that 
API, you can use `raw` values (and switch back to `logical` units as desired).
"Raw" refers to an integer between 0 and 65535 that gets transmitted unmodified
to the bulbs. These two actions are equivalent::

  units raw
  time 10000 duration 2500
  hue 30000 saturation 65535 brightness 32767 kelvin 2700 set all

  units logical
  time 10 duration 2.5
  hue 165 saturation 100 brightness 50 kelvin 2700 set all

Note that with raw units, `time` and `duration` are expressed as an integer
number of milliseconds. With logical units, `time` and `duration` are given
as a floating-point quantity of seconds.

There's no limit to the precision of the floating-point value, but because it
will be converted to milliseconds, any digits more than 3 places to the right
of the decimal point will be insignificant. For example, durations of `2` and
`1.9999` are equivalent, while `3` and `2.999` will differ by one millisecond.
However, in practice, none of the timing is precise or accurate enough for you
to see any difference in behavior for these examples. In my experience,
you can't expect precision much better than 1/10 of a second.
