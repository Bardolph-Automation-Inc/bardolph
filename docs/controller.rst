.. _controller:

.. figure:: logo.png
   :align: center

   http://www.bardolph.org

*************************************
Controller and Virtual Machine Module
*************************************

.. contents:: Contents

This document is the first draft of an description of Bardolph's core module
that interprets a script and accesses the lights. It serves as documentation
of some of the program logic, as well as design notes for certain parts of the
code.

If you are trying to use Bardolph, this document won't be of much use to
you. It covers only the internals of the code.

The module builds on a very simple virtual machine that executes a program
built out of a narrow set of instructions, described below.

.. index::
   single: virtual machine
   single: VM registers

VM Architecture
===============
The VM has a set of special-purpose registers. They are:

* hue
* saturation
* brightness
* kelvin
* duration
* first_zone
* last_zone
* power
* name
* operand
* time
* unit_mode

Although each register is expected to have a specific type, in practice each
one is a Python variable and can reference any object.

.. index::
   single: VM instructions

Instructions
============
An *instruction* contains an op-code and maybe parameters. The interesting
instructions are:

* call
* color
* constant
* end
* end_loop
* jsr
* jump
* move
* moveq
* param
* pause
* power
* routine
* stop
* time_pattern
* wait

Units Mode
----------
Both the parser and VM maintain a current units mode. All of the numbers
that appear in the LS code also appear in the generated instructions.

Any numerical values that move from register to register are untouched
as they are copied. Movement between two variables is also done with
no processing.

If a value is moved between a variable and a register, a conversion may
take place. Registers always contain raw values, but variables can contain
either type. If the parser or VM is in logical units mode, then any
value moved out of or into a register must be converted.

Here is an example that illustrates this behavior::

   units logical
   assign x 50
   brightness x          # converted: brightness is 32767

   units raw
   assign x brightness   # x = 32767
   units logical         # no change: x = 32767
   assign x brightness   # x = 50

.. index::
    single: move instruction
    single: moveq instruction

Move - `move` and `moveq`
-------------------------
These are the basic instructions for moving data between registers and
variables.  In a `move` instruction, the source and destination can each
be a variable or a register. The VM determines the appropriate action by
examining the Python type information for `param0` and `param1`.

In a `moveq` instruction, `param0` always contains a fixed value that
the VM will copy directly from the instruction to the destination. The
destination in `param1` can be either a string or an instance of
Register. If the destination is a string, it is interpreted as the
name of a variable. If it is a register, the destination will be the
VM's associated register.

As a source operand, `param0` in a `move` instruction can contain
either a string or an instance of Register. If the source is a Register,
the VM copies the content of the associated register to the destination.
If the source is a string, it is treated as the name of a variable, and
the variable is dereferenced to get the value.

With respect to the destination in `param1`, the `move` instruction
has the same behavior as `moveq`: a string is treated as a variable
name, and a Register object refers to a VM register.

In any case, the VM's CallStack resolves variable names. If a
variable is the destination, the CallStack checks to see if that
variable is in the current stack frame. If so, the value in the stack
frame gets replaced.

If a destination variable name is not in the top stack frame, a value
is added to it, effectively creating a local variable. If the name
is present in the top stack frame, its value is replaced.

If a variable is a source, the VM first looks for it  in the top stack
frame. If that symbol is not there, the VM then checks the globals. If
the symbol isn't in either dictionary, an error has occurred. The parser
should catch that error and report it; if it doesn't, there's a bug in
the parse code.

.. index::
    single: set instruction

Set Color - `set`
-----------------
To execute the `color` command, the VM reads the values from its `hue`,
`saturation`, `brightness`, and `kelvin` registers to assemble a color for the
target device. If the `operand` register contains `light`, the `name` register
is assumed to contain the name of a light. Correspondingly, if `operand`
contains "group" or "location", the `name` register will be treated as the
name of a group or location. Lastly, if `operand` contains "all", the VM
will set all known lights to that color.

.. index::
    single: get instruction

Get Color - `get`
-----------------
This command retrieves current color information from lights themselves and
sets the registers accordingly. The affected registers are hug, saturation,
brightness, and kelvin.

The "operand" register determines the source of the color data. If it contains
`light`, the "name" register is assumed to contain the light's name, and the
colors are retrieved from light with that name. If the "name" register is
empty, all lights are examined, and the arithmetic mean of each setting is
stored in the registers.

If the "operand" register contains `group` or `location`, then the registers
receive the arithmetic mean of the lights belonging to that group or location.

.. index::
    single: power instruction

Set Power - `power`
-------------------
Similar to the `color` instruction, `power` relies on the `operand` and `name`
registers to determine which lights to turn on or off. The content of the
`power` determines whether to turn the lights on or off.
Technically, to remain consistent with the LIFX API, this should be either 0
or 65535. However, the VM will interpret any non-zero or non-False value to
mean turn the lights on, and will send 65535 to the lights. As with the `set`
command, the targetd lights are specified by the content of the `operand`
register.

.. index::
    single: pause instruction

Pause for Keypress - `pause`
----------------------------
Display a message on the console, and wait for the user to press a key. If they
press !, the script will continue to run and ignore any subsequent pause
instructions. Pressing 'q' stops the execution and exits. Any other key resumes
normal execution of the script.

.. index::
    single: disc, discn, discl, discp instruction
    single: lights; discover

Discover Lights - `disc`, `discn`, `discl`, and `discp`
-------------------------------------------------------
Discover the lights on the network. The `operand` register determines what to
look for: lights, groups, or locations. Each mnemonic has a different purpose:

* `disc` - start discover.
* `discn` - get next element in whatever list is being traversed.
* `discl` - start discover, but get the last element instead of the first.
* `discp` - get the previous element.

Typically, `disc` will be used with `discn`, while `discl` and `discp` will
be used together.

A forward iteration process works as follows:

* With a `disc` instruction, get the first element.
* In subsequent `discn` instructions, pass in the last element
  that was returned.

Because the lights are ordered by name, the next light is determinate
and code always processes the lights in the same order.

A reverse iteration works the same. In all the following discussion,
logic using `disc` and `discn` will also work with `discl` and `discp`,
except the iteration will be in reverse order. This is helpful when you
want to push all the lights onto a stack.

For all of these instructions, the `operand` register determines what
information about the lights is obtained.

In all cases the VM instruction has two parameters, but one or both may
contain None. When a parameter in the instruction is None, it is not passed
to the implementation of the mnemonic.

`disc` With No Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^
This returns the first element's name in the `result` register. That element
depends on whther `operand` register is set to `light`, `group`, or `location`.
The first name is put into the `result` register, or None if no lights are
available.

`disc` With One Parameter
^^^^^^^^^^^^^^^^^^^^^^^^^
In this case, the `operand` must contain either `group` or `location`. The
parameter contains the group or location name. The name of the first member
light is returned in the `result` register.

`discn` With One Parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^
This is used when iterating over all lights, or doing a shallow traversal
across all groups or locations. Depending on the content of the `operand`
register, this gets the next light, group, or location. The parameter must
contain the name of the current element. The name is put into the `result`
register, or None if the end has been reached.

`discn` With Two Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Two parameters are used here to iterate over all the lights *within* a
group or location. In this case, the `operand` register must contain `group`
or `location`. The first parameter is the name of the group or location that
is being traversed, and the second parameter is the name of the last light
obtained from that group. The name is put into the `result` register, or None
if the end has been reached.

All Lights
^^^^^^^^^^
To perform some process on all lights:

#. set `operand` register to `all`
#. `disc` command with no parameters.
#. The `result` register contains the name of the current light in
   the iteration.
#. `discn` instruction with the current light as the first parameter.
#. Repeat until the `result` register contains `None`.

To continue to the next light, use `disc` with the name of the first light as
the parameter. Continue the iteration by passing in the most recent name in
each `disc` instruction. When the end of the list has been found, the `result`
register will contain `None`.

Iterate Groups and Locations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To iterate over all of the groups:

#. set `operand` register to `group`
#. `disc` with no parameters
#. The `result` register contains the name of the current group in
   the iteration.
#. `discn` instruction with the current group as the first parameter.
   The next group gets put into the `result` register.
#. Repeat until the `result` register contains `None`.

To iterate within a group:

#. set `operand` register to `group`
#. `disc` with the name of a group in the first parameter.
#. The `result` register contains the name of the current light in
   the iteration.
#. `discn` instruction with the group as the first parameter and the
   current light in the second parameter. The next group gets put into the
   `result` register.
#. This iteration process continues until the `result` register contains
   `None`.

If the `operand` register contains `location`, then locations undergo
processing analagous to the above.

Counting
^^^^^^^^
The `count` command gets the number specified by the contents of the `operand`
register. If `operand` contains `all`, the `result` register gets the total
number of lights.

If the `operand` register contains `group`, `count` with no parameters gives
the number of groups. The `count` command with one parameter treats that
parameter as a group name, and returns the number of lights in that group.

Similar behavior occurs with `location` in the `operand` register.

.. index::
    single: wait instruction

Wait
----
Wait for the given delay to expire. The `time` register can contain
the delay, expressed in milliseconds. If the `time` register contains
a time pattern, then the VM idles until the system time matches the
pattern.

.. index::
    single: operand register

Operand
-------
Setting the `operand` register indicates what the next "set" or "power"
instrucion will affect. Meaningful values for this register are "light",
"group", and "location". If the register is empty, the behavior is undefined.

The content of this register determines the meaning of the contents of the
VM's "name" register, which could be a name of a light, the name of a group, or
location.

.. index::
    single: variables

Variables
---------
A variable can exist in local or global scope. When one is created inside a
routine definition, it exists in local scope and hides any global variable
of the same name.

Parsing Variable Usage
^^^^^^^^^^^^^^^^^^^^^^
In all cases, `param0` is a string containing the name of the variable.

Sequence:

   #. In source code, reach an "assign" command.
   #. Get the name of the variable, in the next token.
   #. Add the variable to the current call context.
   #. and use it as `param1`.
      Note that in all cases, the name of the variable is in `param1`.
   #. Get the next token, which contains the value for the variable.
   #. If the value is a macro or literal, generate a `moveq` instruction
      with the actual value in `param0`. If the value is a register,
      generate a `move` instruction with an instance of Register in `param0`.
      If the value resolves to variable, generate a `move` instruction where
      `param0` is a string containing the name.

Executing Variable Usage
^^^^^^^^^^^^^^^^^^^^^^^^
In a `moveq` instruction, `param0` is aways considered to be a literal
value, including when it is a string.

With this instruction, the VM examines the Python type of
`param1`. If it's a string, `param1` is considered to be the
name of the destination variable. If it is of
type Register, the destination is the VM's associted register.

In a `move` instruction, either parameter can be a string. In all
cases with this instruction, a string is considered a variable name.
Either parameter can also be an instance of Register. Because `param0`
and `param1` can both be either a Register or a string, there are 4
permutations of source/destination types.

When a variable is assigned a value, it is added to the dictionary of
variables at the top of the call stack. This means that any existing
value gets replaced, and new variables are created automatically.

If the currently executing code is not within a routine, the top of
the call stack will effectively point to the root frame, which
contains the global variables.

.. index::
   single: macros

Macros
------
A macro is distinguished from a variable as it is resolved at compile time.
Its value is embedded directly into the instruction. At this point,
variables are unimplemented.

Sequence:
#. In source code, reach `define` statement for value, which can be a string,
number, or time pattern.
#. Save the value of the macro in the call context's globals.

.. index::
   single: routines

Subroutines
-----------
Although other names are available, such as "method" or "function", for this
project, the term "routine" refers to a chunk of code that can be invoked.

A routine definition contains a list of parameter names that also defines their
order. Because call instructions use the name of a routine, the loader in the
VM bears the responsibility of transforming that name to the entry point of
the routine.

Call Context
^^^^^^^^^^^^
The *call context* is used by the *parser*. The purpose of the call context
is to provide information about symbols at compile time. This includes a
Symbol's name, its type and possibly its value.

The global section of the context contains routine and macro definitions.
These values can be resolved at compile time. The context also has a stack,
which handles parameters and their scope.

Within a routine's code, occurances of name tokens yield symbol look-ups.
Given an arbitrary string, the call context can tell whether that symbol
exists, and if it does, what its type and possibly its value are.

A symbol of type `macro` has a concrete value at compile time, which can be
put directly into `param0` of the VM `param` instruction. If a name resolves
to a symbol of type `param`, then `param0` gets a Symbol, also of type `param`,
with a name but no value.

Upon exit, the stack is popped and the routine's parameters go out of scope.

Stack Frame
^^^^^^^^^^^
The *stack frame* is used by the *virtual machine*. It tracks return
addresses for when routines exit, and manages parameters.

Within the code, various `move` instructions copy data from
parameters into VM registers. In these instructions, the "source" in
`param0` contains a Symbol of type `var`. The value for this parameter
is available from the currrent routine's stack frame, at the top of the
stack, or in the global symbol table.

That stack frame is populated by zero or more `param` instructions, each
with a name and a value. Prior to the routine call, those instructions
cause parameters to be accumulated in a dictionary, which serves
as an activation record. The `param` instructions are immediately followed by
a `call` command. A new stack frame with that activation
record gets pushed on top of the stack, where it can be accessed
by `move` instructions in the current routine's code. The
VM then creates a new staging dictionary for any nested routine calls.

Upon exit, the stack frame is popped. The dictionary representing the
activation record should be empty at this point. The stack should never
be empty; in all cases, at least the root frame must be present.

Before any routines are called, the stack has a single stack
frame which represents the root, or global frame. Any effort to
resolve a variable name first checks the top of the stack. If the name
isn't found, the call stack then checks the root frame.

Parsing a Routine
^^^^^^^^^^^^^^^^^
Because nested routine definitions will not be allowed (at first), the call
context should never have a stack longer than one, which means it's not
really a stack. It's just toggling between main code and routine definitions.

Sequence:

#. In the source, reach a `define` statment with name and optional parameter
   list. If parameters are present, put their names into the current call
   context. The order in which they are added determines their order in calls
   to the routine.
#. Push the call context.
#. Add `routine` instruction with name.
#. Code - For data access, the top call context tells whether a name is a
   parameter or macro. If's a parameter, then use a `move` instruction
   with the parameter's name. Otherwise, use `moveq` and put the macro's
   literal value into the instruction. Obtain that constant value from
   the call context.
#. Generate `end` instruction.
#. Pop call context.
#. Store Routine object in call context globals.

Parsing a Call to a Routine
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Each parameter to a routine call can be a literal (number, string, or
time stamp), a reference to a macro, or a Symbol.

#. For each parameter in the routine definition's list, generate a `param`
   instruction.
#. Generate a `call` instruction containing the routine's name in a string.

To set the value of a parameter, a `param` instruction holds
the name of the parameter in `param0`, and `param1` contains the
parameter itself. In the case of a literal, the value can be put
directly into `param0` in the instruction. For a macro, the name
can be resolved through the call context and its value put into
`param0`.

If the parameter is of type `var`, then `param1` in the generated `param`
instruction is an instance of Symbol. During execution, upon detecting that
`param1` contains a Symbol, the VM will attempt to resolve it, first
in the call stack, then in its globals.

Running Code
^^^^^^^^^^^^
The output of the parser contains code that is executed immediately, with
routine definitions mixed in. The loader puts the immediate code the
*main* segment while collecting the routine code in a *routine segment*.

Layout of a program after it has been loaded:

#. `jump` instruction to main segment.
#. Routine code.
#. Main code.

With this layout, the program terminates when the VM finishes
executing the last instruction.

Loading:

#. Read instructions into main code segment.
#. `routine` instruction.

   #. New Routine object.
   #. Zero or more `param` instructions - add them to Routine.
   #. Save entry point to Routine
   #. Copy instructions into routines segment.
   #. Add Routine object to symbol table for globals.

#. `end` instruction - continue with copy into main segment.
#. Combine segments into a `jump` instruction followed by a single list.
   Because the main segment follows the routine segment, the address for the
   `jump` instruction is equal to the length of the routine segment.

Executing:

#. Initialize by creating staging stack frame.
#. Start at entry point. Interpret until at end.
#. `param` instruction: put value into staging stack frame.
#. `call` instruction

   #. Push staging frame onto stack (creates a new one as current).
   #. Retrieve Routine object from globals.
   #. Jump to routine address.
   #. Continue executing.
   #. `move` instruction: `param0` contains the name of a variable. Use
      the stack frame to find the value of that variable and move it
      into the register specified by `param1`.
   #. `moveq` instruction: `param0` contains the actual value. Put that
      value directly into the register specified by `param1`.

#. `end` instruction

   #. Get return address from top context.
   #. Pop context off stack.
   #. Jump to return address.

Loops
-----
A counting loop has the syntax::

   repeat <iteration model>
   with <variable>
   from <starting value> to <ending value>

Note that

If `iteration_model` is omitted, the loop is considered infinite, and
repeats until the VM stops executing the code::

   # Repeat until the VM is told to stop executing the code.
   #
   repeat begin
      hue 120 set all
      hue 180 set all
   end

The `iteration_model` can be a symbol, constant, or arithmetic
expression, indicating a discreet number of iterations. The generated
VM code evaluates the limit once, before beginning the loop::

    # Execute the code 5 times.
    #
    repeat 5 begin
        #...
    end

    define five 5
    repeat five begin
        # ...
    end

    # Execute the code 3 times.
    #
    repeat {five - 2} begin
        #...
    end

Iterating over Lights
^^^^^^^^^^^^^^^^^^^^^
(Not implemented, yet. Currently undergoing development) Lastly, the
iteration can occur over a set of lights, locations, or groups. This type
of iteration has one of the following syntaxes:

.. code-block:: lightbulb

    repeat <name> in all
        # do something

    repeat name in groups
        # do something

    repeat name in locations
        # do something

    repeat name in <light set>
        # do something

In the last case, the `<light_set>` placeholder can be replaced with one or more
lights, groups, and locations, connected by `and`::

    repeat the_light in "Top" and "Middle"
        on the_light

    repeat the_light in "Middle" and "Top" and group "Furniture"
        on the_light

The lights are traversed using the order in which they appear in the code.
For example, the top `repeat` first turns on the light "Top", and then
"Middle". In the lower loop, they are turned on in the opposite order.

Within each group, the lights are traversed in alphabetical order of their
names. This guarantees that the order will always be the same.

As an example, to reduce the brightness of all lights by 10%:

.. code-block:: lightbulb

    repeat light in all
    begin
        get light
        brightness {brightness * 0.9}
        if {brightness < 0.1}
            brightness 0
        set light
    end

Range of Values
^^^^^^^^^^^^^^^
The addition of `with` sets up a kind of index variable that is updated
with each loop. The limits given indicate what the first and last desired
values are. Using that and the number of repetitions, the VM evenly divides
the range and sets the varaiable to the interpolated values. For example,
to evenly bring up all the lights from 0% to 100%::

   # Do 10 iterations and distribute the values of brt so that they
   # are spread evenly between 0 and 100.
   #
   repeat 10 with brt from 0 to 100 begin
      brightness brt
      set all
   end

The term `cycle` indicates that the index variable will start at the
given point, and go through one complete rotation of 360 degrees::

   repeat 10 with the_hue cycle 180
      hue the_hue
      set all
   end

In this exmple, `the_hue` starts with a value of 180. It is then incremented
10 times. At the end of the last iteration, `the_hue` contains the value
that comes immediately before 180.

Loop Frame
^^^^^^^^^^
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

Job Scheduling
==============
The controller maintains an internal queue of scripts to execute. When a script
completes, the job scheduler moves on to the next one and launches it. The
process executing the script runs in a separate thread.

By default, when script finishes, the sceduler discards it. When the queue is
empty, the scheduler effectively becomes idle. However, if "repeat" mode is
active, completed scripts are immediately added to the end of the queue. The
effect of this is to repeatedly execute all the scripts indefinitely until
a stop is requested.
