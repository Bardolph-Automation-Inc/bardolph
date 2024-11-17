Functions (unimplemented)
=========================

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
