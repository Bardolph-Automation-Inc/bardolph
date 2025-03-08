
.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. index::
    single: array

.. _array:

***************
Bardolph Arrays
***************

An array is declared with the ``define`` keyword. After it has been defined,
the elements can be accessed with numerical subscripts. The language
specification allows for arrays to have an arbitrary dimension.
The size and dimension of an array are static and set when the
array is declared. For example, to declare a one-dimensional vector:

.. code-block:: lightbulb

    define vector[5]

In this example, the array named `vector` has 5 elements and can be accessed
with subscripts from 0 to 4.

Once an array is declared, it can be written with ``assign`` and read wherever
any other variable is allowed.

.. code-block:: lightbulb

    define hues[10]
    assign hues[5] 120

    hue hues[5]

Accessing an array with a subscript that is negative or outside the bounds of
its size will cause an error to be logged, but in most cases, the virtual
machine will make an attempt to provide a reasonable default. If the subscript
is a floating-point value, the fraction will be truncated to yield an integer.

To declare a multi-dimensional array, use a series of square brackets, each
with a size. For example:

.. code-block:: lightbulb

    define colors[8][4][9]
    assign colors[1][3][8] 100

Within the declaration, the desired size of the array can be calculated at
run-tme. As with other features of the language, numerical expressions need to
be in curly braces.

.. code-block:: lightbulb

    define hue_array[{hue / 10}]

    assign n {j + 5}
    define int_array[n]

Assigning an array to a variable creates an alias and does not make a copy:

.. code-block:: lightbulb

    define mat[3]
    assign mat[0] 100
    assign mat2 mat
    assign mat2[0] 200

    # This will print 200
    print mat[0]

When an array is partially subscripted, the result is itself an array with
a reduced dimension.

.. code-block: lightbulb

    define array[5][5][5]

    assign matrix array[4]
    assign matrix[0][0] 100

    assign vector array[4][2]
    assign vector[0] 200

Iterating Over an Array
-----------------------
To iterate over a specific range, use the ``repeat`` ``with`` construct:

.. code-block: lightbulb

    define vector[5]

    repeat with i from 1 to 3
        assign vector[i] {i * 2}

To iterate over all of the elements in an array, use a ``repaeat`` ``in``
``as`` clause:

.. code-block: lightbulb

    define hues[3]

    assign h 0
    repeat in hues as hues_element begin
        assign vector_element h
        assign h {h + 120}
    end

A similar construct can be used for multi-dimensional arrays:

.. code-block: lightbulb

    define colors[5][3]

    repeat in colors as color
        repeat in color as setting
            assign setting 0

    assign color_vector colors[0]
    repeat in color_vector as setting
        assign setting 1


Design Overview
===============
