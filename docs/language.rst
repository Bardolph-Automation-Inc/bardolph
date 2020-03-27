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
During execution, the Bardolph virtual machine sends these settings
to the lights.

One easy way to understand the meaning of these numbers is to use
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

.. index::
    pair: color setting; definition
    pair: color; definition

.. note:: The term *color* is somewhat ambiguous. Intuitively, you may
  consider brightness (intensity) to be separate from a bulb's color.
  However, for simplicity here, "color" always refers
  to the tone of the light and its intensity. Therefore,
  in this documentation, "setting the color" of a light means that
  you are specifying both the frequency and the brightness of the
  light that the device produces.

  Throughout this documentation, *color setting* is defined as any of
  the parameters that control this so-called color. The available
  color settings are `hue`, `saturation`, `brightness`, and `kelvin`.

Syntax
======
A script is a plain-text file in which all whitespace is equivalent. You can
format it with tabs or even put the entire script on a single line.
Comments begin with the '#' character and continue to the end of the line. All
keywords are in lower-case text. By convention, script file names have the
".ls" extension, meaning "lightbulb script".

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
  pair: name; syntax

Names
-----
As described below, the language supports various features that make use of
symbolic names. Examples of this are variables and macros. A valid name
starts with either an underscore or alphabetic character. The rest of the
name can contain letters, numbers, and underscores. For example:

* `x`
* `_living_room`
* `Bulb_80`

Names are handled with case-sensitive logic.

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
Scripts can be much terser with shorthand color setting names: `h` (hue),
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
#. Turn on all the lights, but ramp up the brightness over a period of 1.5
   seconds.
#. Wait 5 seconds again.
#. Dim down the light named "Table" over a period of 1.5 seconds until it
   is off.

The underlying API has a precision down to milliseconds. For example, all
digits are significant in a `time` parameter of `1.234`.

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
before the virtual machine is ready for the next instruction. In this case,
that instruction gets executed without any timer delay. If delay times are too
short for the program to keep up, it will simply keep executing
instructions as fast as it can.

.. index::
  single: clock time
  single: time of day
  single: time pattern
  pair: time pattern; syntax

Wait for Time of Day
=====================
Instead of waiting for a delay to elapse, you can specify the specific time
thatan action occurs, using the `at` modifier with the `time` command. For
example, to turn on all the lights at 8:00 a.m.::

  time at 8:00 on all

All times are specified using a 24-hour clock, with midnight at 0:00.
In this documentation, the parameter supplied in the script is called
a *time pattern*.

A time pattern can contain wildcards to match more than one possible
time. For example, to turn on the lights on the hour and turn them off on the
half-hour::

  time at *:00 on all time at *:30 off all

A time pattern can have placeholders for one or two digits with an
asterisk. Here are some examples of valid patterns:

* `2*:00` - matches 21:00, 22:00, and 23:00.
* `1:*5` - matches 1:05, 1:15, 1:25, 1:35, 1:45 and 1:55.
* `*:30` - matches on the half-hour.

These are not valid patterns:

* `*` or `*:*` - matches anything and is therefore meaningless.
* `12:8*` - not a valid time.
* `**:08` - only one asterisk is necessary.
* `12:5` - minutes need to be expressed as two digits.

Note that the language is procedural, not declarative. This means that the
script is executed from top to bottom. For example, assume you run this script
at 8:00 a.m.::

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
The script adds a 200-second wait to keep it from exiting before that slow
`set` completes. If a script is waiting in the queue, this prevents that next
script from starting before the 200-second duration has elapsed.

Groups and Locations
====================
The `set`, `on`, and `off` commands can be applied to groups and locations.
For example, if you have a location called "Living Room", you can turn them
on and set them all to the same color with::

  on location "Living Room"
  hue 120 saturation 80 brightness 75 kelvin 2700
  set location "Living Room"

Continuing the same example, you can also set the color of all the lights in
the "Reading Lights" group with::

  set group "Reading Lights"

You can combine lights, groups, and locations with the `and` keyword::

  set location "Living Room" and "Table" and group "Reading Lights"

.. index::
   pair: define; macro
   single: macro

Macro Definitions
=================
A macro can be defined to hold a commonly-used name or number::

  define blue 240 define deep 100 define dim 20
  define gradual 4
  define ceiling "Ceiling Light in the Living Room"
  hue blue saturation deep brightness dim duration gradual
  set ceiling

A macro can be used for a light name or a value to be used to set a
parameter. It can also be used as a zone number with multi-zone
lights::

  define my_light "Chair Side"
  hue 120 saturation 80 brightness 50 kelvin 2700
  set my_light

  define zone_1 5 define zone_2 10
  set "Strip" zone zone_1 zone_2

Macros may refer to other existing macros::

  define blue 240
  define b blue

A macro can be defined only once, which makes it suitable for constants::

  define blue 240
  define blue 260 # Error: already defined.

.. index::
  single: variables
  pair: assign; syntax

Variables
=========
A variable is somewhat similar to a macro, in that it can hold a value.
However, a variable's contents can be replaced with a new value at
run-time. In addition, the current value for a color setting can be
copied into a variable. The syntax is:

  `assign variable value`

A variable can contain a number, a string, or a time pattern. Once
it has been initialized, it can be used as a name or a value for a
color or time setting. For example::

  assign the_light "Chair"
  on the_light

  assign the_room "Living Room"
  off group the_room

  assign dinner_time 17:00
  time at dinner_time on "Table"

An existing variable can be assigned to another. A variable can also get
a copy of a color setting. For example::

  assign x 120
  assign y x     # y now contains 120
  hue 240
  assign y hue   # y now contains 240

Assignment of one variable to another has by-value semantics::

  assign x 120
  assign y x
  assign x 240    # y still contains 120
  hue y           # Sets hue to 120.

In this example, `y` has an independent copy of the original value of `x`,
even after `x` has been given a new value.

.. index::
  single: mathematical expressions
  single: numeric operations

Mathematical Expressions
========================
An expression can be used wherever a number is needed. The syntax
for an expression is to contain it in curly braces. For example, to
put 5 + 4 into x::

  assign x {5 + 4}

The syntax for an expression is a narrow subset of that of numerical
expressions in Python. It can contain numbers, references to variables,
registers, and the standard operators `+`, `-`, `*`, `/`, and `()`.
Currently, no mathematical functions are available.

Registers can provide values::

  assign double_brt {brightness * 2}
  brightness double_brt
  brightness {double_brt / (2 + 10)}

  assign double_brt {double_brt - 10}

.. index::
  pair: define; routine
  single: subroutine

Routine Definitions
===================
A subprogram, hereafter called a *routine* can be defined as a
sequence of commands. Here's a simple exmple of a routine being defined
and called::

  define shut_off_all off all
  shut_off_all

A routine can have one or more parameters delineated by the `with` and
`and` keywords::

  define set_mz with mz_light and mz_zone
    set mz_light zone mz_zone

  set_mz "Strip" 7

Note that the routine's parameters are separated by the `and` keyword
only in the definition. Neither `with` nor `and` appear in the
routine call.

If a routine contains multiple commands, they need to be contained
in `begin` and `end` keywords::

  define partial_shut_off begin
    off group "Living Room"
  end

  define off_3_seconds with the_light begin
    duration 3
    off the_light
  end

  partial_shut_off
  off_3_seconds "Chair"

A routine can call another and pass along incoming parameters. As noted
above, the parameters are passed by value::

  define delayed_off with light_name and delay begin
    time delay
    off light_name
  end

  define slow_off with light_name and delay begin
    duration 30
    delayed_off light_name delay
  end

  slow_off "Chair" 10

A routine may not be re-defined. Routine definitions may not be nested::

  define a_routine set "Chair"
  define a_routine set "Table"  # Error: already defined.

  define outer
    begin
      # Error: nested definition not allowed.
      define inner on all
    end

Variables defined inside a routine are local and go out of scope when the
routine returns. Because parameters are passed by value, assignment to a
parameter overwrites the local copy but does not affect any variable
outside of the routine::

  define do_brightness with x begin
    assign x 50     # Overwrite local copy.
    brightness x    # Set brightness to 50.
  end

  assign y 100
  do_brightness y
  saturation y      # y unchanged: set saturation to 100.

Variables assigned outside of a routine are considered global and are
visible in all scopes::

  assign y 100

  define set_global begin
    assign y 50
  end

  set_global
  saturation y   # Set saturation to 50.

.. index::
   single: conditional
   single: if

Conditionals
============
A conditional consists of the `if` keyword, followed by an expression and
one or more commands. It can also have an `else` clause::

  if {x < 5} off all

  get "Top"
  if {hue < 100} begin
    hue 100
    set "Top"
  end

  if {x >= 5} begin
     on all
     hue 120 set all
  end else begin
     off all
  end

.. index::
   single: loops
   single: repeat

Repeat Loops
============
An infinitely repeating loop looks like::

  repeat
    begin
      on all
      off all
    end

Thoretically, this loop will run forever. However, the job control for the VM
is designed to support graceful cutoff of a script's execution. For ambient
interior lighting, this is expected to be a common use case.

To repeat a loop a given number of times::

  repeat 10
    begin
      on all
      off all
    end

The interpolated values in a loop allow you to choose the starting and
ending points for the lights and the number of steps to take in
between. For example, to give a light a hue of 120, and then gradually
transition it to 180 in 5 steps::

  repeat 5 with the_hue from 120 to 180
    begin
      hue the_hue
      set all
    end

In this example, `the_hue` will have values of 120, 135, 150, 165, and 180.

You an use `repeat while` for a loop based on a logical condition::

  repeat while {x < 10}
  begin
    on all
    off all
    assign x {x + 1}
  end

A special use case is to cycle the hue 360° over multiple iterations,
perhaps in an infinite loop. The `cycle` keyword causes a value to loop
around with modulo 360 logic, stopping one step short of a complete cycle.
This keeps the delta between sequential repetitions equal to the increment
used by the loop as it updates the index variable. For example::

  repeat
    repeat 4 with the_hue cycle
      begin
        hue the_hue
        set all
      end

The inner loop gets executed 4 times, with `the_hue` having values of
0, 90, 180, and 270, the difference being 90°. The next time the
loop executes, it starts again at 0, which is equivalent to 360°. This
effectively picks up where the previous loop left off.

You can also specify the starting point::

  repeat 4 with the_hue cycle 45
  # etc.

In this case, `the_hue` will have values of 45, 135, 225, and 315.

.. index::
   single: get
   single: retrieving colors

Retrieving Current Color
========================
The `get` command retrieves the current settings from a single light::

  get "Table"
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

When in logical mode, a value moved between a variable and a setting
is subject to conversion. Following is an example that illustrates this
behavior. Note that 50% in logical units is equivalent to 32767 in raw
units::

  units logical
  brightness 50
  assign x brightness   # x contains 50.

  units raw             # x still contains 50.
  assign x brightness   # x now contains 32767.
