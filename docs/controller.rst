.. _controller:

.. figure:: logo.png
   :align: center

   http://www.bardolph.org

Controller Module
#################
This document is the first draft of an description of Bardolph's core module
that interprets a script and accesses the lights. It serves as documentation
of some of the internals, as well as design notes for certain parts of the
code.

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
* end
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

Move and Moveq
--------------
These are the basic instructions for moving data into registers. In
both cases, the source is in `param0` of the instruction and the
desitnation register is in `param1`. The difference between the two
lies in the meaning of `param0`.

In a `move` instruction, `param0` is a string containing the name of a
symbol. When the VM executes this instruction, it first checks the list
of parameters, which are in the top stack frame. If that
symbol is not there, the VM then checks the globals. In either case, the
dictionary must contain the value of the symbol. If the symbol isn't in
either dictionary, an error has occurred. The parser should catch
that error and report it.

Until variables have been implemented, no globals will exist.

In a `moveq` instruction, `param0` contains the actual value, which was
known at compile time. A string in this case is considered a literal value.
Execution copies the content of `param0` directly from
this instruction into the register.

Set Color - color
-----------------
To execute the "color" command, the VM reads the values from its `hue`,
`saturation`, `brightness`, and `kelvin` registers to assemble a color for the
target device. If the `operand` register contains `light`, the `name` register
is assumed to contain the name of a light. Correspondingly, if `operand`
contains "group" or "location", the `name` register will be treated as the
name of a group or location. Lastly, if `operand` contains "all", the VM
will set all known lights to that color.

Get Color - get
---------------
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

Set Power - power
-----------------
Similar to the `color` instruction, `power` relies on the `operand` and `name`
registers to determine which lights to turn on or off. The content of the
`power` determines whether to turn the lights on or off.
Technically, to remain consistent with the LIFX API, this should be either 0
or 65535. However, the VM will interpret any non-zero or non-False value to
mean turn the lights on, and will send 65535 to the lights. As with the `set`
command, the targetd lights are specified by the content of the `operand`
register.

Pause for Keypress - pause
--------------------------
Display a message on the console, and wait for the user to press a key. If they
press !, the script will continue to run and ignore any subsequent pause
instructions. Pressing 'q' stops the execution and exits. Any other key resumes
normal execution of the script.

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
Setting the "operand" register indicates what the next "set" or "power"
instrucion will affect. Meaningful values for this register are "light",
"group", and "location". If the register is empty, the behavior is undefined.

The content of this register determines the meaning of the contents of the
VM's "name" register, which could be a name of a light, the name of a group, or
location.

.. index::
   single: routines

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
~~~~~~~~~~~~
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
~~~~~~~~~~~
The *stack frame* is used by the *virtual machine*. It tracks the return
address for when a the routine exits, and manages parameters.

Within the code, various `move` instructions copy data from
parameters into VM registers. In these instructions, the "source" in
`param0` contains a Symbol of type `var`. The value for this parameter
is available from the currrent routine's stack frame, at the top of the
stack, or in the global symbol table.

That stack frame is populated by zero or more `param` instructions, each
with a name and a value. Prior to the routine call, those instructions
cause parameters to be accumulated in a dictionary, which serves
as an activation record. When the VM gets to the `call` command, that
dictionary defines all of the parameters
associated with that routine. A new stack frame with that activation
record gets pushed on top of the stack, where it is accessed by the current
routine's code. The VM then creates a new one for the subsequent routine
calls.

Upon exit, the stack frame is popped. The dictionary representing the
activation record should be empty at this point.

Parsing a Routine
~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each parameter to a routine call can be a literal (number, string, or
time stamp), a reference to a macro, or a Symbol.

#. For each parameter in the routine definition's list, generate a `param`
   instruction.
#. Generate a `call` instruction containing the routine's name in a string.

In all cases, `param0` in the instruction contains the name of the parameter
and `param1` contains the parameter itself. In the case
of a literal, the value can be put directly into `param0` in the
instruction. For a macro, the name can be resolved through the call context
and its value put into `param0`.

If the parameter is of type `var`, then `param1` in the generated
instruction would be an instance of Symbol.
During execution, when param1 contains a Symbol, the VM will attempt to
resolve it, first in its parameter dictionary, then in its globals.

Running Code
~~~~~~~~~~~~
The output of the parser contains code that belongs in the main segment, with
routine definitions mixed in.

Layout of a program after it has been loaded:

#. `jump` instruction to main segment.
#. Routine code.
#. Main code.

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

.. index::
   single: job scheduling

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
