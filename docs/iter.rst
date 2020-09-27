
.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. _iteration:

***************************************************
Iterations with the Bardolph Language (in progress)
***************************************************
This article is incomplete and being worked on. Please see the secion on
"Repeat Loops" in :ref:`language` for more information.

Introduction
============
This article provides an introduction the `repeat` command in Bardolph's
programming language.

Iterations in this language are designed for use cases aprpopos to lights.
Specifically, they are built around the notion of a cue, which is a state
that you want one or more lights to have. Because of this,
iterations can provide a variable that is interpolated between cycles, as
opposed to one that is incremented with each repetition.

Interpolated Values
-------------------
For example, suppose you want all the lights to slowly rise from complete
darkness to full intensity, and you want it to happen over the period of
an hour. One way to accomplish this is with:

.. code-block:: lightbulb

    brightness 0
    set all
    duration {60 * 60}
    brightness 100
    set all

However, in practice, I wouldn't necessarily recommend sending an hour-long
command to all the light bulbs. A more reliable method is to break it up,
sending a command to the lights every 5 minutes:

.. code-block:: lightbulb

    define five_min {5 * 60}
    time five_min duration five_min
    repeat 12 with brt from 0 to 100 begin
        brightness brt
        set all
    end

Notice that the values for `brt` are interpolated between the first and last
values. An equivalent, but messier and approach would be to use a more
traditional form of a loop:

Iterating Over Lights
---------------------
For some uses, it's helpful to iterate over all of the lights, accessing
each one individually. For example, as a test, you might want to turn on each
light for 2 seconds and turn it off again. You can do this with:

.. code-block:: lightbulb

    repeat all as the_light begin
        time 0
        on the_light
        time 3
        off the_light
    end

By adding interpolation to this kind of iteration, you can distribute a
range of values across a set of lights, distributed evenly.

Suppose you want to set all your lights to a range of hues between 100 and 140.
In addition, you want change only each light's hue, but keep the brightness
and saturation the same:

.. code-block:: lightbulb

    repeat all as the_light with the_hue from 100 to 140
    begin
        get the_light
        hue the_hue
        set the_light
    end

In this case, the run-time system uses the number of lights on the network
to calculate a delta and assign evenly-distributed values to `the_hue`.
