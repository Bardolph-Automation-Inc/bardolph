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

.. index:: virtual machine, VM; registers

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
* pc (program counter)
* result
* time
* unit_mode

Although each register is expected to have a specific type, in practice each
one is a Python variable and can reference any object.

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
    single: operand register

Operand Register
----------------
Many instructions can be applied to either a light, group, or location. By
setting the `operand` register, you specify what any subsequent command should
be applied to. Defined values for this register are `light`,
`group`, and `location`.

The content of this register often specifies the meaning of the contents of the
"name" register, which could be a name of a light, a group, or a location.

.. index:: VM; instructions

Instructions
============
Although no assembler is available, it's convenient to think of a VM's program
as a set of machine instructions. An *instruction* contains an op-code and
maybe parameters. The list of instructions, which would be considered mnemonics
in an assembly language, is represented by Enum `bardolph.vm.OpCode`.

This section covers some of the instructions that I needed to document for
myself while working on the VM.

Move - `move` and `moveq`
-------------------------
These are the basic instructions for moving data between registers and
variables.  In a `move` instruction, the source and destination can each
be a variable or a register. The VM determines the appropriate action by
examining the Python type information for `param0` and `param1`.

In a `moveq` instruction, `param0` always contains a literal value that
the VM will copy directly from the program code to the destination.

The destination in `param1` can be either a string or an instance of
Register. If the destination is a string, it is interpreted as the
name of a variable, and the value is assigned to that variable. If the
destination is a Register object (which is an Enum), the destination will
be the VM's corresponding register.

In the case of a `move` instruction, `param0` is assumed to contain a
reference to a value, as either a string or an instance of Register. If
the source is a Register, the VM copies the content of the corresponding
register to the destination. If the source is a string, it is treated
as the name of a variable, and the variable is dereferenced to get the value.

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

Set Color - `color`
-------------------
To execute the `color` command, the VM reads the values from its `hue`,
`saturation`, `brightness`, and `kelvin` registers to assemble a color for the
target device. If the `operand` register contains `light`, the `name` register
is assumed to contain the name of a light. Correspondingly, if `operand`
contains "group" or "location", the `name` register will be treated as the
name of a group or location. Lastly, if `operand` contains "all", the VM
will set all known lights to that color.

Get Color - `get_color`
-----------------------
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

Jump to Address - `jump`
------------------------
In order to keep the code relocatable, all `jump` instructions have relative
addresses. To effect the jump, the VM adds an offset, which may be negative,
to the `pc` register.

Each instruction has a condition that controls the behavior of the jump. Those
conditions are defined in the `JumpCondition` enum in `vm/vm_codes.py`. In this
context, the term "truthy" describes an object for which the Python `bool()`
function would `True`.

* `ALWAYS`: jump unconditionally. Add `param1` from the instruction to the `pc`
    register.
* `IF_FALSE`: if the `result` register is not truthy, add `param1` to the `pc`
    register.
* `IF_TRUE`: if the `result` register is truthy, add `param1` to the `pc`
    register.
* `INDIRECT`: jump unconditionally, but treat `param1` as the name of a variable
    and get the offset by dereferencing that variable.

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

Pause for Keypress - `pause`
----------------------------
Display a message on the console, and wait for the user to press a key. If they
press !, the script will continue to run and ignore any subsequent pause
instructions. Pressing 'q' stops the execution and exits. Any other key resumes
normal execution of the script.

Discover Lights - `disc`, `discm`
---------------------------------
Discover the lights on the network. The `operand` register determines what to
look for: lights, groups, or locations. Each mnemonic has a different purpose:

*   `disc` - start discover. Takes no parameters, and uses the content of the
    `operand` register to choose lights, groups, or locations.
*   `dnext` - get next element in whatever list is being traversed, again
    determined by the content of the `operand` register. The first
    parameter contains the current element.
*   `discm` - start discovering members within a group or location. Takes one
    parameter, which is the name of a group or a location, as specified by the
    `operand` parameter.
*   `dnextm` - get the next element within a group or location. The first
    parameter is the name of the group/location, and the second parameter is
    the current member.

All Lights
^^^^^^^^^^
To perform some process on all lights:

#. set `operand` register to `lights`.
#. `disc` command.
#. The `result` register now contains the name of the current light in
   the iteration.
#. `dnext` instruction with the current light name as the first parameter.
#. Repeat until the `result` register contains `None`.

Iterate Groups and Locations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To iterate over all of the groups:

#. set `operand` register to `group`
#. `disc` command.
#. The `result` register now contains the name of the current group in
   the iteration.
#. `dnext` instruction with the current group as the first parameter.
   The next group gets put into the `result` register.
#. Repeat until the `result` register contains `None`.

To iterate within a group:

#. set `operand` register to `group`
#. `discm` with the name of a group in the first parameter.
#. The `result` register contains the name of the current light in
   the iteration.
#. `dnextm` instruction with the group as the first parameter and the
   current light in the second parameter. The next group gets put into the
   `result` register.
#. This iteration process continues until the `result` register contains
   `None`.

To access locations: to iterate locations, use a process similar to the one
above, but put `location` into the `operand` register.

Wait
----
Wait for the given delay to expire. The `time` register can contain
the delay, expressed in milliseconds. If the `time` register contains
a time pattern, then the VM idles until the system time matches the
pattern.

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

Macros
------
A macro is distinguished from a variable as it is resolved at compile time.
Its value is embedded directly into the instruction. At this point,
variables are unimplemented.

Sequence:
#. In source code, reach `define` statement for value, which can be a string,
number, or time pattern.
#. Save the value of the macro in the call context's globals.

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

.. index:: VM; I/O, VM; out instruction, VM; in instruction

I/O
===
Aside from access to lights, I/O has been deliberatley absent. A small `VmIo`
module enables simple output to `stdout`.

Syntax
------
Output is accomplished with one of the following commands:

* ``print``: print a single value, followed by a space.
* ``println``: print a single value, followed by a newline.
* ``printf``: formatted output with zero or more parameters.

For example:

.. code-block:: lightbulb

    print brightness
    print {saturation / 100}
    printf "Currently: {} {} {} {}\n" hue saturation brightness kelvin

Note that ``print`` can take only one value, while ``printf`` takes an arbitrary
number. Because the number of parameters depends on the
format string, that string must be either a literal or macro, known at
compile time.

Support for the format specifier should be fairly complete, including placement
by name:

.. code-block:: lightbulb

    printf "Currently: {kelvin} {} {} {}\n" hue saturation brightness kelvin
    printf "Currently: {1} {0} {3} {2}\n" hue saturation brightness kelvin

In terms of data format, all numeric values are floats in RGB and logical
mode, and integers in raw mode. Light names are strings. Any variables and
register names can appear within the format specifier, and expressions are
anonymous:

.. code-block:: lightbulb

    printf "Currently: {kelvin} {} \n" {brightness / 100.0} kelvin

VM Implementation
-----------------
All access to the I/O module is done via the ``out`` instruction. If I ever add
input, it will likely be with an ``in`` instruction. The format of an ``out``
instruction is `out <target> <payload>`. The `<target>` parameter can be one of:

* `IoOp.UNNAMED`: the payload is a chunk of data to be output as an unnamed
    value.
* `IoOp.NAMED`: the payload is the value to associate with the name contained
    in that string. For example, if the string is "x", then the value of the
    variable `x` is to be output. This may include register names, such as
    `kelvin` or `brightness`.
* `IoOp.PRINT`: the payload is sent to `stdout` via Python's `print()` function.
* `IoOp.PRINTF`: the payload is a string containing a format specfier that will
    be passed to the `str.format()` method. The accumulated data is output.

For example, this script:

.. code-block:: lightbulb

    print kelvin
    printf "Data: {x} {kelvin} {} {}" x kelvin 5 saturation

could yield the following instructions::

    out IoOp.PRINT Register.KELVIN

    out IoOp.NAMED "x"
    out IoOp.NAMED Register.KELVIN
    out IoOp.UNNAMED 5
    out IoOp.UNNAMED Register.SATURATION
    out IoOp.PRINTF "Data: {kelvin} {} {}"
