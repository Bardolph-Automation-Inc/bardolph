.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. index::
   single: language reference

.. _language:

******************
Language Reference
******************

This page describes the syntax and capabilities of Bardolph's scripting
language. For information on how to run a script, please see
:ref:`command_line`.

Internally, launching a script is a two-step process. First, a parser reads the
source file and compiles it into a sequence of encoded instructions. Next, a
simple virtual machine executes those instructions. A job-control facility
maintains a queue, allowing execution of a sequence of compiled scripts.

.. index:: color; set for all

Syntax
======
A script is a plain-text file in which all whitespace is equivalent. You can
format it with tabs or even put the entire script on a single line.
Comments begin with the '#' character and continue to the end of the line. All
keywords are in lower-case text. By convention, script file names have the
".ls" extension, meaning "lightbulb script".

Here's an example, showing some comments

.. code-block:: lightbulb

    # comment
    hue 360 # red
    saturation 100    # 100% saturation
    brightness 60.0   # 60% brightness
    kelvin 2700

    set all

This script sets the colors of all known lights to a bright shade of red.
Note that the ``set`` command is what actually causes the lights to adopt the
new settings and change their colors. The ``all`` parameter causes the given
settings to be applied to all of the lights found on the network.

A script sets the color and brightness of the lights by specifying
5 numbers: ``hue``, ``saturation``, ``brightness``, ``kelvin``, and ``duration``.
During execution, the Bardolph virtual machine sends these settings
to the lights.

The value you supply for ``hue`` is an angle expressed in
in degrees, normally between 0 and 360. The values for ``saturation``
and ``brightness`` are treated as percentages, while ``kelvin`` is considered
a temperature in °K. The value for ``duration`` is expressed in
seconds, and tells the light how long to take to transition from its current
state to the one you are now specifying. If you never supply a value for
``duration``, it defaults to zero, and transitions occur instantaneously.

All of these numbers except ``hue`` must be positive, and may be floating-point
values. Percentages above 100 are considered invalid. Angles for ``hue``
greater than or equal to 360 are normalized to a number less
than 360 by modulo arithmetic.

One easy way to see what colors correspond to these numbers is to use
the color wheel in the LIFX mobile app. In that app, you can see values for hue,
saturation, and brightness in real time. If you wanted to reproduce a color, you
could put the values displayed by the app into a script.

.. index:: color; definition of term

.. note:: The term *color* is somewhat ambiguous. Intuitively, you may
  consider brightness (intensity) to be separate from a bulb's color.
  However, for simplicity here, "color" always refers
  to the tone of the light and its intensity. Therefore,
  in this documentation, "setting the color" of a light means that
  you are specifying both the frequency and the brightness of the
  light that the device produces.

  Throughout this documentation, *color setting* is defined as any of
  the parameters that control this so-called color. The available
  color settings are ``hue``, ``saturation``, ``brightness``, and ``kelvin``.

When a setting isn't specified a second time, the VM uses the existing value.
For example, the following reuses numbers for ``saturation``, ``brightness``,
and ``kelvin``:

.. code-block:: lightbulb

  hue 120 saturation 100 brightness 50 kelvin 2700 set all
  hue 180 set all

This script will:

#. Set all lights to HSBK of 120, 100, 50, 2700
#. Set all lights to HSBK of 180, 100, 50, 2700

Any uninitialized values default to zero, or an empty string. This can lead
to unwanted results, so each of the values should be set at least once before
setting the color of any lights. Or, consider starting your script with
`get all` (the ``get`` command is described below).

.. index:: name syntax

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

.. index:: lights; individual, lights; set color, color; set for light

Individual Lights
=================
Scripts can control individual lights by name. For example, if you have a light
named "Table", you can set its color with:

.. code-block:: lightbulb

  hue 120 saturation 100 brightness 75 kelvin 2700
  set "Table"

A light's name is configured when you do initial setup with the LIFX software.

When they appear in a script, bulb names must be in quotation marks. They
can  contain spaces, but  may not contain a linefeed. For example:

.. code-block:: lightbulb

  # Ok
  on "Chair Side"

  # Error
  on "Chair
  Side"

If a script contains a name for a light that has not been discovered or is
otherwise unavailable, an error is sent to the log, but execution of the script
continues.

.. index:: multi-zone lights, lights; multi-zone

Multi-Zone Lights
=================
With multiple-zone lights, the ``set`` command works the same,
but you can limit which zones it affects. It can set all of
them to the same color, set the color of a single zone, or set
it for a range of them. For example, I have a Z LED strip, which
I named "Strip". I can set the entire device to one color with:

.. code-block:: lightbulb

  hue 150 saturation 100 brightness 50 kelvin 2700 duration 1.5
  set "Strip"

To set only one zone, add a ``zone`` clause with a single number:

.. code-block:: lightbulb

  set "Strip" zone 5

To set multiple zones, specify a range with starting and ending
zone numbers:

.. code-block:: lightbulb

  set "Strip" zone 0 8

Note that the zone numbers start with zero. If you try use a zone on
a light that doesn't have that capability, an error will be sent to
the log, and the light will not be accessed. Unlike Python ranges, the
numbers are inclusive. For example, `zone 1 3` would include zones 1, 2,
and 3.

.. index:: power

Power Command
=============
The commands to turn the lights on or off resemble the ``set`` command:

.. code-block:: lightbulb

  off all
  on "Table"

This turns off all the lights, and turns on the one named "Table".

The ``on`` and ``off`` commands have no effect on the color of the lights.
When ``on`` executes, each light will have whatever its color was when
it was turned off. If a light is already on or off, an otherwise
redundant power operation will have no visible effect, although the
VM does send the power command to the bulbs.

When applied to a multi-zone light, the entire device is powered
on or off; you can't set the power for individual zones (although you
can set the brightness to zero).

.. index:: abbreviations

Abbreviations
=============
Scripts can be much terser with shorthand color setting names: ``h`` (hue),
``s`` (saturation), ``b`` (brightness), and ``k`` (kelvin). The following two
lines do the same thing:

.. code-block:: lightbulb

  hue 180 saturation 100 brightness 50 kelvin 2700 set all
  h 180 s 100 b 50 k 2700 set all

.. index:: timing

Timing Color Changes
====================
Scripts can contain time delays and durations, both of which are are expressed
in seconds. A time delay designates the amount of time to wait before
transmitting the next command to the lights. The duration value is passed
through to the bulbs, and its interpretation is defined by the
`LIFX API <https://lan.developer.lifx.com>`_. Basically, by setting a duration,
you determine how long it should take the bulb to transition to its new
state. For example

.. code-block:: lightbulb

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
digits are significant in a ``time`` parameter of `1.234`.

As mentioned above, the existing values for ``time`` and ``duration`` are re-used
with each command. In this example, ``time`` is set only
once, but there will be the same delay between every action.

Multiple Lights Using `and`
---------------------------
If you want to set multiple lights at the same time, you can chain them using
``and``

.. code-block:: lightbulb

  time 2 on "Table" and "Chair Side"  # Uses "and".

This script will:

#. Wait 2 seconds.
#. Turn both lights on *simultaneously*.

This contrasts with:

.. code-block:: lightbulb

  time 2 on "Table" on "Chair Side"   # Does not use "and".

This script will:

#. Wait 2 seconds.
#. Turn on the light named "Table".
#. Wait 2 seconds.
#. Turn on the light named "Chair Side".

The ``and`` keyword works with ``set``, ``on``, and ``off``. When multiple lights are
specified this way, the interpreter attempts to change all of the lights at
once, with (theoretically) no delay between each one.

If a script specifies zones, the ``and`` comes after the zone numbers. This
can be convenient for coordinating a multi-zone light with single-zone
bulbs. For example, with a multi-zone light named "Strip" and a bulb named
"Table"

.. code-block:: lightbulb

  hue 120 saturation 75 brightness 75 kelvin 2700 duration 1.5
  set "Strip" zone 0 5 and "Table"

Here's an example of simultaneously setting multiple zones on the
same light:

.. code-block:: lightbulb

  set "Strip" zone 2 and "Strip" zone 13 15

How Time Is Measured
====================
It's important to note that delay time calculations are based on when
the script started. The delay is not calculated based on the completion
time of the previous instruction.

For example:

.. code-block:: lightbulb

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

.. index:: clock time, time of day, time pattern

Wait for Time of Day
=====================
Instead of waiting for a delay to elapse, you can specify the specific time
that an action occurs, using the ``at`` modifier with the ``time`` command. For
example, to turn on all the lights at 8:00 a.m.:

.. code-block:: lightbulb

  time at 8:00 on all

All times are specified using a 24-hour clock, with midnight at 0:00.
In this documentation, the parameter supplied in the script is called
a *time pattern*.

A time pattern can contain wildcards to match more than one possible
time. For example, to turn on the lights on the hour and turn them off on the
half-hour

.. code-block:: lightbulb

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
at 8:00 a.m.:

.. code-block:: lightbulb

  time at 10:00 on all
  time at 9:00 off all

This will turn on all the lights at 10:00 a.m., wait 23 hours, and turn them
off again the next day.

You can combine patterns to create more complicated behavior. For example, this
will turn on the lights the next time it's either 15 or 45 minutes past the
hour:

.. code-block:: lightbulb

  time at *:15 or *:45 on all

After a scheduled wait, the delay timer is essentially reset. For example:

.. code-block:: lightbulb

  time at 12:00 on all
  time 60 off all

This would turn on all the lights at noon and then turm them off 60 seconds
later, which would be at 12:01 p.m.

.. index:: pause, keypress

Pause for Keypress
==================
Instead of using timed delays, a script can wait for a key to be pressed. For
example, to simulate a manual traffic light

.. code-block:: lightbulb

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
timer is reset. For example:

.. code-block:: lightbulb

  time at 12:00 on all
  pause off all
  time 10 on all

This script turns on all the lights at 12:00 noon. It then waits
for the user to press a key at the keyboard. When a key has been pressed,
it turns off all the lights, waits 10 s, and turns them on again.

.. index:: groups, locations

Wait With No Action
===================
To wait for the next time interval without doing anything:

.. code-block:: lightbulb

  wait

This can be useful to keep a script active until the last command has been
executed. For example:

.. code-block:: lightbulb

  time 0 hue 120 saturation 90 brightness 50 kelvin 2700
  duration 200 set all
  time 200 wait

In this example, the ``set`` command will take 200 seconds to fully take effect.
The script adds a 200-second wait to keep it from exiting before that slow
``set`` completes. If a script is waiting in the queue, this prevents that next
script from starting before the 200-second duration has elapsed.

Groups and Locations
====================
The ``set``, ``on``, and ``off`` commands can be applied to groups and locations.
For example, if you have a location called "Living Room", you can turn them
on and set them all to the same color with:

.. code-block:: lightbulb

  on location "Living Room"
  hue 120 saturation 80 brightness 75 kelvin 2700
  set location "Living Room"

Continuing the same example, you can also set the color of all the lights in
the "Reading Lights" group with:

.. code-block:: lightbulb

  set group "Reading Lights"

You can combine lights, groups, and locations with the ``and`` keyword:

.. code-block:: lightbulb

  set location "Living Room" and "Table" and group "Reading Lights"

.. index:: macro, define; macro

Macro Definitions
=================
A macro can be defined to hold a commonly-used name or number:

.. code-block:: lightbulb

  define blue 240 define deep 100 define dim 20
  define gradual 4
  define ceiling "Ceiling Light in the Living Room"
  hue blue saturation deep brightness dim duration gradual
  set ceiling

A macro can be used for a light name or a value to be used to set a
parameter. It can also be used as a zone number with multi-zone
lights:

.. code-block:: lightbulb

  define my_light "Chair Side"
  hue 120 saturation 80 brightness 50 kelvin 2700
  set my_light

  define zone_1 5 define zone_2 10
  set "Strip" zone zone_1 zone_2

Macros may refer to other existing macros:

.. code-block:: lightbulb

  define blue 240
  define b blue

A macro can be defined only once, which makes it suitable for constants:

.. code-block:: lightbulb

  define blue 240
  define blue 260 # Error: already defined.

.. index:: variables, assignment

Variables
=========
A variable is somewhat similar to a macro, in that it can hold a value.
However, a variable's contents can be replaced with a new value at
run-time. In addition, the current value for a color setting can be
copied into a variable. The syntax is:

  `assign variable value`

A variable can contain a number, a string, or a time pattern. Once
it has been initialized, it can be used as a name or a value for a
color or time setting. For example:

.. code-block:: lightbulb

  assign the_light "Chair"
  on the_light

  assign the_room "Living Room"
  off group the_room

  assign dinner_time 17:00
  time at dinner_time on "Table"

An existing variable can be assigned to another. A variable can also get
a copy of a color setting. For example:

.. code-block:: lightbulb

  assign x 120
  assign y x     # y now contains 120
  hue 240
  assign y hue   # y now contains 240

Assignment of one variable to another has by-value semantics:

.. code-block:: lightbulb

  assign x 120
  assign y x
  assign x 240    # y still contains 120
  hue y           # Sets hue to 120.

In this example, `y` has an independent copy of the original value of `x`,
even after `x` has been given a new value.

.. index:: mathematical expressions, numeric operations

Mathematical Expressions
========================
An expression can be used wherever a number is needed. The syntax
for an expression is to contain it in curly braces. For example, to
put 5 + 4 into x:

.. code-block:: lightbulb

  assign x {5 + 4}

The syntax for an expression is a narrow subset of that of numerical
expressions in Python. It can contain numbers, references to variables,
registers, and the standard operators ``+``, ``-``, ``*``, ``/``, and ``()``.
Currently, no mathematical functions are available.

Registers can provide values:

.. code-block:: lightbulb

  assign double_brt {brightness * 2}
  brightness double_brt
  brightness {double_brt / (2 + 10)}

  assign double_brt {double_brt - 10}

.. index:: routine, subourtine, define; routine

Routine Definitions
===================
A subprogram, hereafter called a *routine* can be defined as a
sequence of commands. Here's a simple exmple of a routine being defined
and called:

.. code-block:: lightbulb

  define shut_off_all off all
  shut_off_all

A routine can have one or more parameters if the name is followed by the ``with``
keyword:

.. code-block:: lightbulb

  define set_mz with mz_light mz_zone
    set mz_light zone mz_zone

  set_mz "Strip" 7

If a routine contains multiple commands, they need to be contained
in ``begin`` and ``end`` keywords:

.. code-block:: lightbulb

  define partial_shut_off
  begin
    off group "Living Room"
  end

  define off_3_seconds with the_light
  begin
    duration 3
    off the_light
  end

  partial_shut_off
  off_3_seconds "Chair"

A routine can call another and pass along incoming parameters. The called
routine must already be defined; there currently is no support for forward
declarations. As noted above, the parameters are passed by value:

.. code-block:: lightbulb

  define delayed_off with light_name delay
  begin
    time delay
    off light_name
  end

  define slow_off with light_name delay
  begin
    duration 30
    delayed_off light_name delay
  end

  slow_off "Chair" 10

A routine may not be re-defined. Routine definitions may not be nested:

.. code-block:: lightbulb

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
outside of the routine:

.. code-block:: lightbulb

  define do_brightness with x
  begin
    assign x 50     # Overwrite local copy.
    assigh y 50     # Local variable
    brightness x    # Set brightness to 50.
  end

  assign x 200
  assign y 100
  do_brightness y
  hue x             # x unchanged: set hue to 200.
  saturation y      # y unchanged: set saturation to 100.

Variables assigned outside of a routine are considered global and are
visible in all scopes:

.. code-block:: lightbulb

  assign y 100

  define set_global
  begin
    assign y 50
  end

  set_global
  saturation y   # Set saturation to 50.

.. index:: conditional, if

Functions
=========
A routine can return a value, effectively becoming a so-called function. The
return value can be a variable, macro, constant, or expression.

.. code-block:: lightbulb

    # Function definition
    define max_rgb begin
        assign max red
        if {green > max}
            assign max green
        if {blue > max}
            assign max blue
        return max
    end

    # Function call
    brightness max_rgb

A function may take parameters, using the same syntax as a routine to declare
them:

.. code-block:: lightbulb

    define sum with x and y and z begin
        return {x + y + z}
    end

    define average with x and y and z begin
        return {sum x y z / 3}
    end

You evaluate a function with a syntax similar to that of a routine call:

.. code-block:: lightbulb

    brightness average red green blue

If a parameter consists of multiple tokens, it needs to be contained in curly
braces, much like an expresstion:

.. code-block:: lightbulb

    brightness average {sum 10 20 30} green blue


If a function is called within a mathematical expression, it must be contained
in parentheses:

.. code-block:: lightbulb

    brightness {(average red green blue) / 2}

    brightness {(average red green blue / 2)}
    brightness {(average red green (blue / 2))}

To enhance readability, you may want to add parentheses:

.. code-block:: lightbulb

    brightness {(average red green blue) / 2}
    brightness {(average red green blue) / (average 10 20 30)}

Note that expressions may be passed as parameters, including function calls:

.. code-block:: lightbulb

    assign x {average average 1 2 3 average 4 5 6 7}

    # More readable version:
    assign x {average (average 1 2 3) (average 4 5 6) 7}

A function can return a string, although currently the lanugage doesn't have
any support for string manipulation:

.. code-block:: lightbulb

    define pick_light with x begin
        if {x == 1}
            return "Chair Lamp"
         else if {x == 2}
            return "Table Light"
        return "Bedroom Light"
    end

    on pick_light 3

Note that a light's name can also be returned by a function. In this example,
a function finds the name of the brightest light, which is used to turn it off.

.. code-block:: lightbulb

    define brightest begin
        max_brightness = -1
        repeat all as light begin
            get light
            if {brightness > max_brightness} begin
                assign brightest_light light
                assign max_brightness brightness
            end
        end
        return brightest_light
    end

    off brightest_light

Conditionals
============
A conditional consists of the ``if`` keyword, followed by an expression and
one or more commands. It can also have an `else` clause:

.. code-block:: lightbulb

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

.. index:: loops, repeat, repeat; infinite loop, iteration

Repeat Loops
============
An infinitely repeating loop looks like:

.. code-block:: lightbulb

  repeat
    begin
      on all
      off all
    end

Thoretically, this loop will run forever. However, the job control for the VM
is designed to support graceful cutoff of a script's execution. For ambient
interior lighting, this is expected to be a common use case.

Use `repeat while` for a loop based on a logical condition:

.. code-block:: lightbulb

  repeat while {brightness < 50}
    begin
        brightness {brightness + 0.1}
        set all
    end

To repeat a loop a given number of times:

.. code-block:: lightbulb

  repeat 10
    begin
      on all
      off all
    end

.. index:: interpolation in loops, repeat; with interpolation

Interpolation in Loops
----------------------
Interpolation of values in a loop allows you to choose the start and
end points for a setting and the number of steps to take in
between. For example, to give a light a hue of 120, and then gradually
transition it to 180 in 5 steps:

.. code-block:: lightbulb

  repeat 5 with the_hue from 120 to 180
    begin
      hue the_hue
      set all
    end

In this example, `the_hue` will have values of 120, 135, 150, 165, and 180.

A special use case is to cycle the hue 360° over multiple iterations,
perhaps in an infinite loop. The `cycle` keyword causes a value to loop
around with modulo 360 logic, stopping one step short of a complete cycle.
By starting at zero again, the iteration continues smoothly.

.. code-block:: lightbulb

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

You can also specify the starting point:

.. code-block:: lightbulb

  repeat 4 with the_hue cycle 45
  # etc.

In this case, `the_hue` will have values of 45, 135, 225, and 315.

An arithmetic expression can take the place of any numeric value
in a `repeat` loop. You designate such an expression by enclosing it in
curly braces. For example:

.. code-block:: lightbulb

    assign x 7
    repeat {5 + x} with y from {x * 4} to {x * 6}
    ...

    # Equivalent to:
    repeat 12 with y from 28 to 42
    ...

Note that the loop limit is calculated only once. In the following example,
the loop is executed 5 times, even though `light_count` is modified in the
body of the loop.

.. code-block:: lightbulb

    assign light_count 5
    repeat light_count begin
        # Doesn't affect the number of iterations.
        assign light_count 0
        ...
    end

If you want to control the number of iterations dynamically, you can use a
`repeat while` construct.

.. index:: iteration by light, repeat; for every light

By Light
--------
To iterate individually over all the lights:

.. code-block:: lightbulb

    # Turn on all the lights, one-by-one
    repeat all as the_light
        on the_light

In this example, `the_light` is a variable that is initialized to the name
of the next light before the body of the loop is executed.

A range of values can be applied to the lights. For example:

.. code-block:: lightbulb

    repeat all as bulb with brt from 10 to 30
    begin
        brightness brt
        set bulb
    end

In this case, the number of lights available determines what increment should
be added to the index variable, `brt`. This allows you to distribute a set of
values across some lights without knowing how many there are.

For example, if you have 3 lights, the above loop will be executed 3 times,
with `brt` having values of 10, 20, and 30. If you have 5 lights, you get
5 iterations, with `brt` having values of 10, 15, 20, 25, and 30.

.. index:: groups; iterating all, locations; iterating all

All groups or locations can be enumerated:

.. code-block:: lightbulb

    repeat group as the_group with the_hue from 120 to 180 begin
        hue the_hue
        set group the_group
    end

.. index:: groups; iterating within, locations; iterating within

To iterate over all the lights in a location or group:

.. code-block:: lightbulb

    repeat in location "Inside" as the_light
        on the_light

    repeat in group "Background" as the_light with sat from 70 to 100
    begin
        saturation sat
        set the_light
    end

Individual lights can be part of a list:

.. code-block:: lightbulb

    repeat
        in "Top" and "Middle" and "Table" as the_light
        with sat from 80 to 100
    begin
        get the_light
        saturation sat
        set the_light
    end

They can also be mixed with the members of groups and locations:

.. code-block:: lightbulb

    repeat
        in "Table" and location "Living Room"
        as the_light
        with brt from 10 to 80
    begin
        brightness brt
        set the_light
    end

Here's an example of a nested loop executed for every known group:

.. code-block:: lightbulb

    repeat group as grp with brt from 40 to 80 begin
        repeat in group grp as light with c_hue cycle begin
            hue c_hue
            set light
        end
    end

This loop assigns a different brightness to each group, ranging between 40%
and 80%. Within each group, every light gets the same brightness, but their
hues are distributed evenly across a 360° range.

.. index:: get, retrieving colors, color; get from light, lights; get color

Retrieving Current Color
========================
The `get` command retrieves the current settings from a single light:

.. code-block:: lightbulb

    get "Table"
    set all

This script retrieves the values of `hue`, `saturation`, `brightness`,
and `kelvin` from the bulb named "Table Lamp". It then sets all the
other lights to the retrieved color. This has the effect of setting the
color of all the lights to match "Table".

A useful pattern for this command is to get a light's current values, modify
one of them, and then update the light. This allows you to effectively change
only one setting:

.. code-block:: lightbulb

    get light
    brightness 100
    set light

In this example, the light goes to full intensity withou changing colors.

From a multi-zone light, you can retrieve the color of a single zone or
the entire device:

.. code-block:: lightbulb

    get "Strip" zone 5
    get "Strip"

Note that you cannot get values for locations, groups, multiple zones,
or multiple lights:

.. code-block:: lightbulb

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
    single: units; raw
    single: RGB units
    single: units; RGB
    single: logical units
    single: units; logical

Raw, Logical, and RGB Units
===========================
For me, the HSB coordinate system isn't especially intuitive. For example, if
I want bright green lights, I'll have to look up an angle for the hue, or
maybe memorize which angle corresponds to which percieved color. The RGB color
space can make this much easier, because I know what red, green and blue look
like.

.. index:: RGB units; using

Using RGB
---------
By specifing certain values for red, green, and blue, you can probably make a
pretty good prediction of how a color will look. Most people know that a mix
of red and green yields yellow, green plus blue gives you cyan, and
red with blue produces purple.

With RGB units, each component's intensity is expressed as a percentage, which
can be given as a floating-point number. For example, to make all your lights a
somewhat dim purple, you could have:

.. code-block:: lightbulb

    units rgb
    red 50 green 0 blue 50
    set all

As another example, to have white light that is rather bright:

.. code-block:: lightbulb

    units rgb
    define brt 80
    red brt green brt blue brt

Internally, the VM converts these values to their HSB equivalents before
sending them to the lights.

Note that the setting for `kelvin` works the same for RGB units as it does
for the default logical units. In practiced, I've found that it's easy to
just set `kelvin` to 2700 at the top of the script and not bother with it after
that.

.. index:: raw units; using

Using Raw Units
---------------
In the case of logical or RGB units, numerical values in scripts are given in
units that are intended to be convenient to humans. However, during
communication with the lights, those numbers are mapped to unsigned, 16-bit
integer values as specified by the `LIFX API <https://lan.developer.lifx.com>`_.

If you prefer to send unmodified numbers to the lights as specified by that
API, you can use raw values (and switch back to logical units as desired).
"Raw" refers to an integer between 0 and 65535 that gets transmitted unmodified
to the lights. These two actions are equivalent:

.. code-block:: lightbulb

    units raw
    time 10000 duration 2500
    hue 30000 saturation 65535 brightness 32767 kelvin 2700 set all

    units logical
    time 10 duration 2.5
    hue 165 saturation 100 brightness 50 kelvin 2700 set all

Note that with raw units, `time` and `duration` are rounded to an integer
number of milliseconds. With logical or RGB units, `time` and
`duration` are treated as a floating-point number of seconds.

There's no limit to the precision of the floating-point value, but because it
will be converted to milliseconds, any digits more than 3 places to the right
of the decimal point will be insignificant. For example, durations of `2` and
`1.9999` are equivalent, while `3` and `2.999` will differ by one millisecond.
However, in practice, none of the timing is precise or accurate enough for you
to see any difference in behavior for these examples. In my experience,
you can't expect precision much better than 1/10 of a second.

.. index:: units; switching modes

Switching Unit Modes
--------------------
In general, you'll probably just pick a mode at the top of your script and
not change it. However, if a script does switch modes, some values get
re-calculated to preserve the effect on the lights. For example,
`hue` containing 180 in logical units is converted to 32,767 in raw units.

Which settings get changed depends on what kind of transition takes place. For
example, when switching from RGB to logical units, there's no need to
convert `time` or `duration`. However, `hue`, `saturation`, and `brightness`
are initialized, based on the current values of `red`, `green`, and `blue`.

The following table lists which settings are overwritten, and which ones are
unaltered, based on what kind of switch occurs:

.. list-table:: Changed When Switching Units Mode
    :header-rows: 1
    :widths: 12 11 11 11 11 11 11 11 11

    *   - From
        - To
        - time, dur.
        - hue
        - sat.
        - brt.
        - red
        - green
        - blue
    *   - `logical`
        - `raw`
        - √
        - √
        - √
        - √
        - —
        - —
        - —
    *   - `raw`
        - `logical`
        - √
        - √
        - √
        - √
        - —
        - —
        - —
    *   - `rgb`
        - `raw`
        - √
        - √
        - √
        - √
        - —
        - —
        - —
    *   - `raw`
        - `rgb`
        - √
        - —
        - —
        - —
        - √
        - √
        - √
    *   - `rgb`
        - `logical`
        - —
        - √
        - √
        - √
        - —
        - —
        - —
    *   - `logical`
        - `rgb`
        - —
        - —
        - —
        - —
        - √
        - √
        - √

None of the changes in unit mode affect the contents of ``kelvin``. That value
is always considered to be a temperature measured in °K, and never requires
conversion.

.. note:: While in RGB mode, you can still set the values of ``hue``,
    ``saturation``, or ``brightness``. However, this will have no practical effect;
    when you set the color of a light, the VM will ignore them. The transition
    from RGB to logical or raw mode overwrites the contents of ``hue``,
    ``saturation``, and ``brightness``. Conversely, you can set ``red``,
    ``green``, or ``blue``, but they are unused if the VM is not in RGB mode.
    Similarly, switching to RGB from logical or raw mode overwrites anything
    previously stored in those three settings.

Following is an example that illustrates some of this behavior:

.. code-block:: lightbulb

    units logical
    kelvin 2500
    time 1.5 duration 1.5
    hue 120 saturation 100 brightness 100

    units rgb
    # red, green, and blue are overwritten:
    #   kelvin = 2500
    #   time = 1.5
    #   duration = 1.5
    #   red = 0
    #   green = 100
    #   blue = 0
    #   hue = 120
    #   saturation = 100
    #   brightness = 100


    time 2.5 duration 3.5
    red 0 green 0 blue 100
    hue 0 saturation 0 brightness 0
    units raw
    # time, duration, hue, saturation, brightness are overwritten:
    #   time = 2500
    #   duration = 3500
    #   red = 0
    #   green = 0
    #   blue = 100
    #   hue = 43690
    #   saturation = 65535
    #   brightness = 65535
    #   kelvin = 2500


.. index:: print

Outputting Text
===============
Three commands, ``print``, ``println``, and ``printf``, send output to `stdout`.
They all call Python's own `print` function, which under most conditions sends
text to `stdout`, typically the user's terminal emulator.

Because this is not a general-purpose language, the support for text output
is a fairly rudimentary implementation. I pretty much passses data along to the
underlying Python `print` function, aided by the `string.format` method.

You can print any of the settings, such as ``hue`` or ``brightness``, as well
as variables and constants.

The ``print`` and ``println`` commands take a single parameter, which is
evaluated and sent to `stdout`. The ``print`` command appends a space to its
output, while ``println`` and ``printf`` each append a line feed.

For example to output some settings:

.. code-block:: lightbulb

    hue 120 saturation 50 brightness 75 kelvin 2000
    println "-----"
    print hue
    print saturation
    print brightness
    println kelvin
    println "-----"

This would generate the output::

    -----
    120 50 75 2000
    -----

.. index:: printf

Formatted Output
----------------
For any kind of non-trivial output, you'll probably want to use ``printf``,
which is a pass-through to Python's `string.format()` function.

The ``printf`` command has the syntax::

    printf <format> [param, ...]

For example, to output the settings:

.. code-block:: lightbulb

    hue 120 saturation 50 brightness 75 kelvin 2000
    printf "{} {} {} {}" hue saturation brightness kelvin

Note that the field placeholders, in the form of `{}` correspond to the
parameters.

Because the compiler relies on the format string to determine the number of
parameters, it must be either a literal or a macro.

.. code-block:: lightbulb

    define fmt "{}"
    printf fmt hue
    printf "{}" hue

    assign fmt2 "{}"
    printf fmt2 hue   # ERROR. Must be a literal or a macro.

 It's possible to use named fields, which can give you cleaner code:

.. code-block:: lightbulb

    printf "{hue} {saturation} {brightness} {kelvin}"

Named fields can be mixed with anonymous ones:

.. code-block:: lightbulb

    printf "{hue} {saturation} {brightness} {}" kelvin

The output can contain variables and expressions:

.. code-block:: lightbulb

    assign x 100
    assign y 200
    printf "{x} {} {}" y {(x + y) / 2}

The output can also contain light names. Here's an example that
iterates over all of the lights, and outputs the settings for each one:

.. code-block:: lightbulb

    repeat all as light begin
        get the_light
        printf "Light: {the_light} {hue} {saturation} {brightness} {kelvin}"
    end

The formatting capabilities impelemented by the Python language are rather
extensive and complicated. For more information on how this formatting works,
I recommend that you consult the Python documentation:
https://docs.python.org/3/library/string.html#formatspec

In terms of data types, note that ``hue``, ``saturation``, ``brightness``,
and ``kelvin`` are floating-point numbers in logical and RGB modes. In
raw mode, these values are integers. Here's an example where the light
settings are displayed, first in raw units, and then in RGB units:

.. code-block:: lightbulb

    define header_fmt "{:<9}{:>9}{:>9}{:>9}{:>9}"

    units raw
    println "----- Raw -----"
    printf header_fmt "Name" "Hue" "Sat" "Brt" "Kelvin"
    repeat all as light begin
        get light
        printf "{light:<9}{hue:>9d}{saturation:>9d}{brightness:>9d}{kelvin:>9d}"
    end

    units rgb
    println ""
    println "----- RGB -----"
    printf header_fmt "Name" "Red" "Green" "Blue" "Kelvin"
    repeat all as light begin
        get light
        printf "{light:<9}{red:>9.2f}{green:>9.2f}{blue:>9.2f}{kelvin:>9.2f}"
    end

Notice that the upper ``printf`` uses a format of `:>9d`, which outputs
number as decimal integers, right-justified in a field 9 characters long. The
RGB numbers are output with 2 decimal points.

When I ran this script on my own lights one evening, I got this output::

    ----- Raw -----
    Name           Hue      Sat      Brt   Kelvin
    Bottom       42597    65535    20001     2400
    Middle       38957        0    40259     2700
    Top          35316    65535    56432     2700

    ----- RGB -----
    Name           Red    Green     Blue   Kelvin
    Bottom        0.00     3.05    30.52  2400.00
    Middle       61.43    61.43    61.43  2700.00
    Top           0.00    66.02    86.11  2700.00

Examples with `printf`
----------------------
This code illustrates equivalent behavior using different parameters:

.. code-block:: lightbulb

    printf "{hue} {saturation} {brightness}"
    printf "{} {} {}" hue saturation brightness
    printf "{hue} {} {}" saturation brightness
    printf "{2} {1} {0}" brightness saturation hue

All of these lines produce the same output. Note that the bottom line in the
code uses positional fields, which are a feature of the underlying Python
implementation.

Because of the data types of the settings, use of any integer type specifier
requires raw mode:

.. code-block:: lightbulb

    units raw
    printf "{:d}" hue   # Ok because hue is an integer in raw mode
    printf "{:f}" hue   # Ok because an integer can be converted to float

    units logical
    printf "{:d}" hue   # ERROR: hue is a floating-point number

Note that light names are Python strings:

.. code-block:: lightbulb

    println "Furniture group:"
    repeat in group "Furniture" as light
        printf "{light:>10s}"

    println "Pole group:"
    repeat in group "Pole" as light
        printf "{light:>10}"
