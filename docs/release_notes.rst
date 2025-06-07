.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. index::
   single: Release Notes

.. _release_notes:

*************
Release Notes
*************
In all cases, you can also assume that there were some bug fixes and code
clean-up, although I don't log most bugs on Github.

June 6, 2025
============
Release: 0.2.8

This is primarily bug fixes and reliability improvements.

Fix the broken ``lsc`` command-line tool.

Fix some problems with the web app, particularly around the capture and
retrieve buttons. Along the way, work on refining the installation instructions
for the web server.

Add a cache for matrix lights (Candle and Tube) so that they don't get asked
for their width and height every time they are found on the network. These
values can't change, and there were frequent problems, especially with the Tube
light, in getting a response. Put in some more checks so that scripts are less
likely to halt if there's a problem with the LAN API.

Add a small code optimizer that shrinks the virtual machine code a little bit.
This should also provide a starting point for more optimizations on the
compiler-generated code.

June 1, 2025
============
Release: 0.2.7

Curly Braces No Longer Required
-------------------------------
Re-work the parser so that numerical expressions no longer need to be in curly
braces. For example,

.. code-block:: lightbulb

    assign x {5 + y}

can now be expressed this way:

.. code-block:: lightbulb

    assgign x 5 + y

Logical Expression Syntax Change
--------------------------------
Use ``||`` in place of ``or``, ``&&`` in place of ``and``, and ``!``
instead of ``not`` in logical expressions. For example, instead of:

.. code-block:: lightbulb

    # Error: "and", "or", "not" no longer used in logical expressions.

    if x > y and not (a > b or c > d )begin
        on all
    end

the script needs to have:

.. code-block:: lightbulb

    # Instead of "or", "and", "not", use "||", "&&", "!"

    if x > y && !(a > b || c > d) begin
        on all
    end

Get Information About Lights
----------------------------
Add the "query" function that reports on the physical characteristics of
devices. This allows a script the find out at runtime:

* If the light is "Color" or "White".
* Whether light is a "Lightstrip", "Beam", etc.
* For strip types of lights, how many zones are available.
* Whether the light is a matrix type of device, such as a Candlelight.
* For matrix lights, how many rows and columns a light has.

For exaple, to treat a light differently, depending on whether it is capable of
changing color:

.. code-block:: lightbulb

    if [query "is-color" light_name] begin
        # Color bulb, so set the hue and saturation.
        hue 120
        saturation 90
        kelvin 2000
    end else begin
        # "White" bulb, can't set the color, so just set the temperature.
        kelvin 2700
    end

Documentation for this function can be found here:
:ref:`query function<query function>`


March 12, 2025
==============
Release: 0.2.6

Add support and documentation for Tube lights
(https://www.lifx.com/products/tube-smart-light). Add a function to generate
random numbers.

March 8, 2025
=============
Release: 0.2.5

Quick bug fix.

March 7, 2025
=============
Release: 0.2.4

This release introduces a small collection of mathematical functions. Underlying
that change is a new subsystem that supports a runtime library and the ability
to write callable routines in Python.

January 17, 2025
================
Release: 0.2.3

This is mostly bug fixes.

January 13, 2025
================
Release: 0.2.2

This is the first release that includes documentation for "candle" type bulbs.
I have been working on that feature for quite a while, but before now I wasn't
ready to suggest that it was usable.

This release also introduces the ability of a routine to return a value; that is
to say, *functions*.

November 18, 2024
=================
Release: 0.2.0

After a long break due to unforseen circumstances, bring the code up-to-date
with the current state of Python and the supporting libraries/modules.

January 12, 2022
================
Release: 0.1.5

Bug fixes. Update documentation and fix broken links.

December 29, 2020
=================
Release: 0.1.3

Implement "break" for loops. Refine print, println, and printf.
