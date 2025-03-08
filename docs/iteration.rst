.. _iteration:

.. figure:: logo.png
   :align: center

   http://www.bardolph.org

**********************
Iteration Design Notes
**********************

For a tutorial introcuction to loops in the language, please see the secion on
"Repeat Loops" in :ref:`language` for more information.

Design Overview
===============
A loop has several parts:

#.  The repeat keyword.
#.  An optional condition which eventually terminates the loop. This can be:

    *   A specific number of iterations. For example:

        .. code-block:: lightbulb

            repeat 10

    *   A logical expression with ``while``. For example:

        .. code-block:: lightbulb

            repeat while {x < 10}
                # Eventually x gets a number >= 10 and the loop terminates.

    If no condition is present, the loop theoretically will repeat forever,
    although in practice the VM will eventually be interrupted within the loop.
#.  An optional collection of devices or sets of devices, each of which is
    accessed through an index variable. That collection can be:

    *   All the lights, with the current light's name in an index variable.
        For example, in this loop, the_light is a variable that contains
        the name of the current light in the iteration:

        .. code-block:: lightbulb

            repeat all as the_light
                # Variable "the_light" contains the name of a light

    *   A specific list of lights. For example, if you have lights named
        "Desk Lamp", "Table", and "Reading Light" and want to turn them all on:

        .. code-block:: lightbulb

            repeat in "Desk Lamp" and "Table" and "Reading Light" as the_light
                on the_light

    *   All the groups or locations, with the group or location's name in
        an index variable. For example:

        .. code-block:: lightbulb

            repeat group as the_group
                # Variable "the_group" contains the name of a group.

            repeat location as the_location
                #  Variable "the_location" contains the name of a location.

    *   All the lights belonging to a group. For example, if you have a group
        called "Ambient Lights":

        .. code-block:: lightbulb

            repeat in group "Ambient Lights" as the_light
                # Variable "the_light" contains the name of a light

    *   All the lights within a location. For example, if you have a location
        called "Living Room":

        .. code-block:: lightbulb

            repeat in location "Living Room" as the_light
                #  Variable "the_light" contains the name of a light.

#.  An optional ``with`` clause containing a range of numeric values that are
    interpolated across the iteration. This is useful if you want to
    evenly distribute a set of colors or brighnesses across multiple devices or
    zones. That range can be:

    *   A range of integers, with an index variable that contains the
        current iteration's value. For example:

        .. code-block:: lightbulb

            repeat with n from 1 to 10
                # Variable "n" contains 1, 2, 3, ..., 10

    *   Specific starting and ending values:

        .. code-block:: lightbulb

            repeat all as the_light with brt from 10 to 100 begin
                brightness brt
                set the_light
            end

    *   A cyclic value, typically used for hue, that uses modulo arithmetic to
        keep a value between 0 and 360. This is useful for cycling through a
        range of colors while keeping brightness and saturation the same. For
        example:

        .. code-block:: lightbulb

            # infinite loop
            #
            repeat
                # Divide the color wheel into 10 hues, and give all the lights
                # each of those colors.
                #
                repeat 10 with the_hue cycle begin
                    hue the_hue
                    set all
                end

Use Cases
=========
This section contains some illustrative use cases that lead to the current
design.

Very Long Duration
------------------
Suppose you want all the lights to slowly rise from complete darkness to full
intensity, and you want it to happen over the period of an hour. One way to
accomplish this is with:

.. code-block:: lightbulb

    brightness 0
    set all
    duration {60 * 60}
    brightness 100
    set all

However, in practice, I wouldn't recommend sending an hour-long command to all
the light bulbs. During that time, one or more lights may lose power, and others
might get switched on.

A more reliable method is to break it up, sending a command to
the lights every 5 minutes:

.. code-block:: lightbulb

    define five_minutes {5 * 60}
    define one_hour {60 * 60}

    time five_minutes
    duration five_minutes

    repeat {one_hour / five_minutes} with brt from 0 to 100 begin
        brightness brt
        set all
    end

Notice that the values for `brt` are interpolated between the first and last
values.

Implementation Notes
====================

Although there are multiple types of loops, they all have roughly the same
overall structure:

#.  Push a new context onto the stack and initialize as appropriate for the type
    of loop.
#.  Determine whether or not to continue iterating. If not, pop the stack and
    jump to the first instruction after the end of the loop code.
#.  Execute the user code inside the body of the loop.
#.  Update any active counter and/or index variables.
#.  Jump back to step 2.

Simple Counted Loop
-------------------
This kind of loop has a number of iterations. For example:

.. code_block:: lightbulb
    repeat 5
        println "Hello"

This simply outputs 5 lines, each containing "Hello".

The generated code puts the value 0 into the counter. At the top of the loop
code, there is a check to see if the counter has exceeded the limit. If it
has, the generated code jumps to the end of the loop. Othewise, it executes
the body of the loop, increments the counter, and jumps back to the beginning
of the loop.

List-Based Loop
---------------
This kind of loop has an ``in`` clause. For example:

.. code_block:: lightbulb
    repeat in "table" and "window" and group "kitchen" as the_light
    begin
        print the_light
    end

The parser generates code to place all of the lights onto the stack. In this
example, the code needs to push all of the lights in group `kitchen`, then,
"windo" and "table". The result is that the lights are on the stack in reverse
order.

While it pushes light names onto the stack, the generated code also maintains
a counter. That counter contains the number of lights that are on the stack.

After loading the stack with the light names, the generated code enters a loop
where it will:

#.  Check the counter. If it is 0, then terminate the loop.
#.  Pop the name of the next light off of the stack and place it into the
    index variable. In the example above, the first light name to come off
    the stack would be "window". It is accessible through variable `the_light`.
#.  Execute the body of the loop. In the example, "window" would be sent to
    the log via the ``print`` command.
#.  Subtract 1 from the counter, and jump up to step 1 to possibly execute
    another iteration.

For literals and variables such as "table" and "window", the name of the light
can be pushed directly onto the stack. For groups and locations, however, the
members of a group or location are not known at compile time. Therefore, the
parser must generate code to locate all the members of a group or location, and
push them onto the stack as well.

Loop Frame
----------
A LoopFrame is a specialized StackFrame that is used with loops. Inside
a loop, some variables go into scope, but none become hidden. Therefore,
a LoopFrame inherits all of the variables contained in its parent frame.
This is done by making a copy of the dictionary containing the
parent frame's variables. When the loop frame exits, no variables go
out of scope.

The index variable remains in scope after the loop exits. At that point,
it contains the value it had during the final iteration. As such, it
exists as a local variable in the current CallContext. The index variable
is handled by the generated code, with no specific VM support.

The loop counter and its limit are not visible to the script code after
they have been initialized. They are attributes of the top LoopFrame.
