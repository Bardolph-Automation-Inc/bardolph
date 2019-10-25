.. _installation:

Bardolph Installation
#####################

.. image:: logo.png

This page contains the full installation instructions, including use
of the web server.

Typically, installation takes one of two forms:

#. Download and install the package.
#. Download the source, build the package, and install it.

Note that Python 3.5 or higher is required in all cases. If your system
defaults to Python 2.x, there's a good chance that you'll need to use
`pip3` instead of `pip`. Notable culprits here are Raspbian and Debian.


Option 1: Built Package
=======================
This is the quickest way to get started. You won't necessarily have the
latest code, but that shoudln't be a problem. To do this kind of installation:

.. code-block:: bash

  pip install bardolph


After this intallation, the `lsc`, `lsrun`, and `lscap` commands should be
available. In addition, if you're planning on using scripts in your Python
code, the bardolph libraries will be available.

If you want to run the web server, you still need the source distribution:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph

  
This distribution also contains some sample scripts that can help you
get started.

Option 2: Build and Install
===========================
This option allows you to modify source code, including the configuration that's
built into the Python code. To do this, you need to have `setuptools` installed.
If necessary:

.. code-block:: bash

  pip install setuptools 

With `setuptools` on your system:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph
  python setup.py bdist 
  pip install dist/bardolph-0.0.12-py3-none-any.whl 

Testing the Installation
========================
To do a quick sanity check:

.. code-block:: bash

  lsrun -h

This should display a help screen. To make sure Bardolph is able to access
your actual bulbs:

.. code-block:: bash

  lscap

The source distribution includes some examples in a directory named `scripts`.
For example:

.. code-block:: bash 

  lsrun scripts/all-on.ls

To run a script without attempting to access any bulbs (for example, if you
don't have any), use the "fakes" option:

.. code-block:: bash 

  lsrun -f scripts/all-on.ls

Uninstalling
============
Uninstall with:

.. code-block:: bash 

  pip uninstall bardolph

Modifying the Configuration
===========================
Under most conditions, there should be no need to modify the configuration.
However, if you need to do so, you have a couple of choices. If you build
and install the source code, you can edit
`bardolph/controller/config_values.py`. That file contains all of the
default settings.

Alternatively, you can specify a configuration file when starting one of
the command-line tools. The `lsrun`, `lsc`, and `lscapture` commands
all accept the `-c` or `--config-file` option. For example:

.. code-block:: bash 

  lsrun -c config.ini scripts/all-on.ls


In this case, `lsrun` will first initialize all of its internal settings. It
will then read the file `config.ini` and replace whateve settings are in that
file. For example, by default, all logging output is sent to the screen.
To override that setting and send output to a log file, you would put the
following content into `config.ini`::

  [logger]
  log_file: /var/log/lights.log
  log_to_console: False

An example file with some candidates for customization are in the source
distribution, in the file `docs/bardolph.ini`. Note that this file is
for documentation purposes only; no configuration file outside of the
default Python code should be necessary.

Web Server Installation
#######################
These instructions focus on installing on a Raspberry Pi.

A key goal for theis project is to produce something that's
genuinely useful on an everyday basis. For me, that's a
local web server which is available 24/7. This means it
should be cheap to buy and consume a small amount of power.

The `Raspberry Pi Zero-W <https://www.raspberrypi.org/products/raspberry-pi-zero-w>`_
has been a good fit for my everyday use. Other Raspberry Pi models will 
work as well, but the Zero-W is among the cheapest, and is entirely capable
enough for this purpose.

The server runs an a basic installation of Raspbian. It also runs on Debian and
MacOS; basically, you need a Python interpreter version 3.5 or higher.

O.S. Setup
==========
This overview assumes you have already done the following, which are outside
the scope of this document:

#. Install Raspbian on your device. For more information, please refer to the
   `Raspbian installation instructions
   <https://www.raspberrypi.org/documentation/installation>`_.
#. Enable WiFi and `ssh` on your device. The server will run without a monitor
   or keyboard attached. For more information, see the
   `Raspberry Pi remote access documentation
   <https://www.raspberrypi.org/documentation/remote-access/ssh/>`_.
   
If your device has a physical ethernet port, you can use a wired
connection, but the bulbs need to be on the same LAN.

By default, Raspbian already has a Python interpreter, so you won't need to
install it. However, for more infirmation on running Python code,
please refer to the
`Raspberry Pi Python documentation
<https://www.raspberrypi.org/documentation/usage/python>`_.

Dedicated User
==============
A special-purpose user is convenient for running the server.
It provides you with a home directory for the Bardolph code, and allows
you to tailor that user's characteristics to running the server.
Therefore, the first steps are to create a user called `lights` and give it
sudo access.

.. code-block:: bash

  adduser lights

I also change the name of the server. In this example, my server will be
"vanya", accessed on the command line and in my browser as
"vanya.local". This can be done with
`raspi-config <https://www.raspberrypi.org/documentation/configuration/raspi-config.md>`_.

Bardolph Distribution
=====================
The first step is to do the installation as described at the top of
this doc, using either `setup.py` or `pip`.

To use the web server, you'll need the source distribution, no matter
which kind of installation you do. You can download it from
https://github.com/al-fontes-jr/bardolph.
As user `lights` from the `/home/lights` directory:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph

This will create a directory named `bardolph` and put the distribution
inside that directory.

Application Server
==================
The Bardolph web UI runs within 
`Flask <https://palletsprojects.com/p/flask>`_. It also uses 
`flup <https://www.saddi.com/software/flup>`_ for its WSGI implementation. 
The core Bardolph code relies on `lifxlan <https://pypi.org/project/lifxlan>`_.
You  can install all these with:

.. code-block:: bash

  pip install Flask flup lifxlan

As of this writing, a default Raspbian distribution defaults to Python 2.7, 
so you may need to `pip3` instead of `pip` throughout. 

HTTP Server Setup
=================
Because Bardolph runs as a WSGI application, multiple options exist for
using a front-end to implement the HTTP protocol. I've settled on lighttpd,
which ships with a module for FastCGI.

Installation of lighttpd is outside the scope of this document. I recommend
visting the `lighttpd website <https://www.lighttpd.net>`_
for more information. However, the basic installation can be done with:

.. code-block:: bash

  sudo apt-get install lighttpd

This also installs `spawn-fcgi`.

To use the lighttpd configuration supplied in the source distribution,
you need create symbolic links to the root of the project, or copy the
congiguration files to `/etc/lighttpd`. I prefer symbolic links, because
the configuration files get updated automatically whenever you refresh
the source code from github.com.

For example, if you downloaded the code from github to ~/bardolph:

.. code-block:: bash

  cd /etc/lighttpd
  sudo cp lighttpd.conf lighttpd.conf.original
  sudo ln -s ~/bardolph/web/server/rpi/lighttpd.conf .
  sudo ln -s ~/bardolph/web/server/common.conf .

Logs Directory
==============
The configuration files in the source distribution assume that all
of the logs, for both the Python app
and web server will go into the directory `/var/log/lights`. Therefore,
as part of your setup, you need to do the following:

.. code-block:: bash

  sudo mkdir /var/log/lights
  sudo chown lights:lights /var/log/lights

This allows processes owned by the `lights` meta-user to write all of the
logs in one place.

Start and Stop the Server
=========================
To start the server, cd to the directory where you pulled down the source
from github.com. From there, you need to start two processes:

#. The web application server, a Python program that implements
   the UI and runs the scripts, plus
#. The `lighttpd` process, which attaches to the Python app via FCGI and then
   services incoming HTTP requests for web pages.

Start the Application Server
============================
From the source distribution directory, for example ~/bardolph:

.. code-block:: bash

  ./start_fcgi

You should do this as the `lights` user. For security purposes, that user should
not have any special privileges, such as `sudo`.

Start the HTTP Server
=====================
By default, the `lighttpd` daemon will already be running. You can restart
it using the new configuration with:

.. code-block:: bash

  sudo /etc/init.d/lighttpd restart


If all goes well, you should be able to access the home page. Because
I've named my server "vanya" with raspi-config, I access it at
http://vanya.local.

Stopping
========
To stop and start the HTTP server in separate steps:

.. code-block:: bash

  sudo /etc/init.d/lighttpd stop
  sudo /etc/init.d/lighttpd start


I don't have an elegant way to stop the FCGI process, so:

.. code-block:: bash

  killall python3

or

.. code-block:: bash

  killall python
