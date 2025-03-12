.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. index:: basic installation, installation; basic

.. _installation:

Basic Installation
##################
This page contains instructions for setting up only the interpreter and
other command-line tools. This is a much simpler installation than setting
up the web server, which is described in :ref:`web_install`.

Because the Bardolph wheel designates
`lifxlan <https://pypi.org/project/lifxlan>`_ as a dependency,
it may also be downloaded and installed.

In order to do the installation on a Raspberry Pi, you should probably first
create a Python virtual environment. This is necessary because that version of
Linux is what's known as an "externally managed environment". For example:

.. code-block:: bash

  python -m venv bardolph-venv
  source bardolph-venv/bin/activate

After the activation, your shell prompt will change and have "(bardolph-venv)"
automatically prepended to it. Note that you will need to activate the virtual
environment with `source bardolph-venv/bin/activate` every time you log in.
Note that "bardolph-venv" is just a suggestion; you may name the the
virtual environment any way you see fit.

For more information about virtual envronments, please see the `official Python
documentation <https://docs.python.org/3/library/venv.html>`_. They are a
complex subject, and an extensive discussion of them is outside the scope of
this document.

With the virtual environment activated, you can install the Bardolph package:

.. code-block:: bash

  pip install bardolph

After this intallation, the `lsc`, `lsrun`, and `lscap` commands will be
available whenever your virtual environment is activated. In addition, if
you're planning on embedding scripts in your own Python program, the Bardolph
support code will be importable.

To get a copy of the sample script files, you should get the full
source tree with:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph

Testing the Installation
========================
To do a quick sanity check:

.. code-block:: bash

    lsrun -h

This should display a help screen. To verify access to your actual lights:

.. code-block:: bash

    lscap

This will discover the lights on the network and output a plain-text report
with the state of each light it finds. If you don't have any lights, but
still want to test the installaton, use fakes, which are software simulations
of real lights:

.. code-block:: bash

    lscap -f

As another quick test, you can try turning all the lights off and on again from
the command line:

.. code-block:: bash

    lsrun -s "off all"
    lsrun -s "on all"

The source distribution includes some examples in a directory
named `scripts`. For example:

.. code-block:: bash

    lsrun scripts/on-all.ls

The `-f` flag works here as well, which allows you to try out scripts
without accessing any actual lights.

Note that the above commands are documented in :ref:`command_line`.

.. index:: installation; upgrade, updating version

Upgrading to Latest Version
===========================
From time to time, the package will be updated with fixes and new features. To
upgrade to the latest verstion:

.. code-block:: bash

    source bardolph-venv/bin/activate
    pip install -U bardolph

.. index:: local build

Alternative: Build and Install
==============================
You can use this process if you want to build from source and install the
local package. In this case, you should still use `pip` as your package
manager, so that you can use it later to remove your build and clean
out unwanted files.

To do this, you need to have
`setuptools <https://pypi.org/project/setuptools>`_ installed.

With `setuptools` on your system:

.. code-block:: bash

    pip install lifxlan setuptools build
    git clone https://github.com/al-fontes-jr/bardolph
    cd bardolph
    python -m build
    pip install --no-index --find-links ./dist bardolph

Note that the invocation `python -m build` creates the `dist` directory. Within
that directory, it creates a `.whl` file containing the new package. When
you run `pip`, it finds that file and installs it. You need to install
`lifxlan` manually because the installation of bardolph is limited to
local files.

Although it isn't necessary, you may want to try running the Python unit tests
to validate your copy of the source code and Python environment:

.. code-block:: bash

    python -m tests.every_test

When you get a newer release of the code, you can upgrade it with:

.. code-block:: bash

    python -m build
    pip install --upgrade --no-index --find-links ./dist bardolph

.. index::
    single: uninstall Bardolph

Uninstalling
============
Uninstall with:

.. code-block:: bash

    pip uninstall bardolph

This will work whether you installed a downloaded package, or built and
installed a package locally. If you are using a virtual environment, you need
to activate it before runnning the uninstall command.

.. index:: lifxlan Library, lifxlan; installation, lifxlan; latest version

.. _lifxlan_setup:

Installing the lifxlan Library
==============================
If you are successfully acccessing all of your devices, you can skip this
section. However if you have a Tube device which is not being discovered, the
following information may be helpful.

All access by Bardolph to the LIFX devices is handled through the lifxlan
library. The source code for that library is on Github, at
https://github.com/mclarkk/lifxlan. A packaged version of the library is
available on PyPi at https://pypi.org/project/lifxlan/. If you install
Bardolph using *pip*, it will automatically install the *lifxlan* package from
PyPi as well.

However, that library contains an internal list of known products, which can be
out of date. Whenever LIFX releases a new product, there is a lag before the
lifxlan library is updated with that product's specifications. This means that a
fairly new type of device may not be discovered.

For example, as of the time of
this writing (March, 2025), the version of *lifxlan* on PyPi does not recognize
Tube devices, such as the
`Tube E26 <https://www.lifx.com/products/tube-smart-light>`_. If a script
attempts to access such a device under these conditions, there will be an
error message about a light not being found, and the script will not work.

In this situation you can probably fix the problem by downloading the latest
source code for *lifxlan* and installing the library from that code.

To do so, first activate your virtual environment. For example:

.. code-block:: bash

    source bardolph-venv/bin/activate

Then, with the virtual environment active, run the following command to remove
the PyPi version of the package:

.. code-block:: bash

    pip uninstall lifxlan

Finally, with the virtual environment still active, run the following commands
from your home directory to install from the latest source code:

.. code-block:: bash

    git clone https://github.com/mclarkk/lifxlan
    cd lifxlan
    python setup.py install

When this is complete, you should be able to see devices that were previously
undiscovered.

Note that there may still be devices that are missing. The definitive list is
available at https://github.com/LIFX/products/blob/master/products.json. If
your device is on that list, but still not handled by *lifxlan*, you may want
to try running generate_products_file.py, although I haven't tried it and
don't recommend it.
