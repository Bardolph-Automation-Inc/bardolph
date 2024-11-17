"Candlelight" Bulbs (under development)
=======================================

The underlying API for these devices are covered in the
`LIFX documentaion <https://lan.developer.lifx.com/docs/candle>`. I've
attempted to make control of this type of bulb relatively straigtforward.
In the Bardolph model, the light has 5 rows, each consisting of 5 zones that
encircle the center axis of the bulb. It also has a `top` element. The rows are
numbered 0 through 4, as are the zones.

The syntax is basically:

.. code-block:: lightbulb

  set <name> row <start> <end> column <start> <end> top

Both `row` and `zone` are optional. Each of them can have either one or two
parameters. The `top` keyword is also optional.

For example, to draw a red vertical line from top row to bottom row of the bulb,
you can use:

.. code-block:: lightbulb

  hue 120 saturation 75 brightness 75
  set "Candle" row 0 4 column 0

Conversely, to draw a horizontal ring around the middle of the light and set
the color at the top:

.. code-block:: lightbulb

  set "Candle" row 2 column 0 5 top

An example of seting a 3x3 square area:

.. code-block:: lightbulb

  set "Candle" row 1 3 zone 0 2

Set just the top of the light:

.. code-block:: lightbulb

  set "Candle" top

If you supply only `column` or only `row`, the full range (0 through 4) of the
unspecified parameter is assumed. For example:

.. code-block:: lightbulb

  set "Candle" row 1 column 0 4
  set "Candle" row 1               # same result

  set "Candle" column 1 3
  set "Candle" column 1 3 row 0 4   # same result
