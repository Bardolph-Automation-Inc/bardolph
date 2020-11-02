.. figure:: logo.png
   :align: center

   http://www.bardolph.org

.. index:: web server; installation, installation; web server

.. _web_install:

***********************
Web Server Installation
***********************
This page contains instructions for installation of the web server.
If you just want to run scripts from the command
lline, please refer to the simpler instructions in :ref:`installation`.

The focus here is installation on a Raspberry Pi. However, the
instructions should be fairly accurate for a typical Debian-based system.

A key goal for this project is to produce something that's
genuinely useful on an everyday basis. For me, that's a
local web server which is available 24/7. This means it
should be cheap to buy and consume a small amount of power.

The `Raspberry Pi Zero-W <https://www.raspberrypi.org/products/raspberry-pi-zero-w>`_
has been a good fit for my everyday use. Other Raspberry Pi models will
work as well, but the Zero-W is among the cheapest, and is entirely capable
enough for this purpose.

The server runs well on a stock installation of Raspbian. It also runs on
Debian and MacOS; basically, you need a Python interpreter revision 3.5 or
higher.

On a typical installation, two separate process will run:

#. The web application server, a Python program that implements
   the UI and runs the scripts, plus
#. The `lighttpd` process, which attaches to the Python app via FCGI and then
   services incoming HTTP requests for web pages.

O.S. Setup
==========
This overview assumes you have already done the following, which are outside
the scope of this document:

#. Install Raspberry Pi OS on your device. For more information, please refer
   to the software installation instructions at
   https://www.raspberrypi.org/documentation/installation. If you're going to
   run a headless server, any installation down to the "Lite" one is
   sufficient.
#. Enable WiFi and `ssh` on your device. The server will run without a monitor
   or keyboard attached. For more information, see the
   `Raspberry Pi remote access documentation
   <https://www.raspberrypi.org/documentation/remote-access/ssh/>`_.

If your device has a physical ethernet port, you can use a wired
connection instead of WiFi, but it needs to be on the same network
that the lights are on.

By default, RPi OS already has a Python interpreter, so you won't need to
install it. However, if you desire more information on running Python code,
please refer to the
`Raspberry Pi Python documentation
<https://www.raspberrypi.org/documentation/usage/python>`_.

Dedicated User
==============
A special-purpose user is convenient for running the server.
It provides you with a home directory for the Bardolph code, and allows
you to tailor that user's characteristics to running the server.
Therefore, the next step is to create a user called `lights`.

.. code-block:: bash

   sudo adduser lights

Note that this user doesn't have any special privileges. This ensures that
the Python code itself runs under a standard account, thus improving
security.

I also change the name of the server. In this example, my server will be
"vanya", accessed on the command line and in my browser as
"vanya.local". This can be done with
`raspi-config <https://www.raspberrypi.org/documentation/configuration/raspi-config.md>`_.

Download Source Tree
====================
The web server relies on many non-Python files that are not part of the
packaged distribution. As a result, you'll need to clone the entire source
tree. First, log in as the `lights` user, then:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph

Install Python Modules
======================
Still logged in as the `lights` user:

.. code-block:: bash

  pip install bardolph

.. note:: Python 3.7 or higher is required in all cases. If your system
   defaults to Python 2.x, you probably need to use
   `pip3` instead of `pip` throughout these instructions. Notable
   culprits here are Raspbery Pi OS and Debian. You may even have to install
   `pip3` itself with `sudo apt-get install python3-pip`.

After this intallation, the `lsc`, `lsrun`, and `lscap` commands will be
placed into your `~/.local/bin` directory, which you should add to your
path.

This installation also publishes Python modules for parsing and executing
scripts.

As of this writing, the default `.profile` on in Raspbian adds `~/.local/bin`
to your path, but only if the directory exists when you log in. Therefore,
either log out and back in again, or:

.. code-block:: bash

  source ~/.profile

If you are using a different operating system, or your `.profile` doesn't
add the path, you'll need to do so yourself.

Testing the Installation
========================
To do a quick sanity check:

.. code-block:: bash

  lsrun -h

This should display a help screen. To make sure Bardolph is able to access
your lights:

.. code-block:: bash

  lscap

For all the bulbs that are discovered, you will see a plain-text table of
their current settings.

.. index::
   single: HTTP Server Setup
   single: lighttpd

HTTP Server Setup
=================
This is the first of several steps that need to be done while logged in as
a user with `sudo` access, such as the default `pi` user.

Because the Bardolph server runs as a
`WSGI <https://wsgi.readthedocs.io>`_ application, multiple options exist for
using a front-end to implement the HTTP protocol. I've settled on lighttpd,
which ships with a module for FastCGI.

Installation of lighttpd is outside the scope of this document. I recommend
visting the `lighttpd website <https://www.lighttpd.net>`_
for more information. However, the basic installation can be done with

.. code-block:: bash

  sudo apt-get install lighttpd

This also installs `spawn-fcgi`.

To use the lighttpd configuration supplied in the Bardolph source
distribution, you need create symbolic links to the root of the project,
or copy the configuration files to `/etc/lighttpd`. I prefer symbolic
links, because the configuration files get updated automatically
whenever you refresh the source code from github.com.

For example, if you downloaded the code from github to `~lights/bardolph`:

.. code-block:: bash

  cd /etc/lighttpd
  sudo mv lighttpd.conf lighttpd.conf.original
  sudo ln -s /home/lights/bardolph/web/server/rpi/lighttpd.conf .
  sudo ln -s /home/lights/bardolph/web/server/common.conf .

.. index::
   single: web logging configuration

Log Directory Setup
-------------------
This is another step you take as a user with `sudo` access, such as the
`pi` default user.

The web site configuration files in the source tree specify
that all of the logs reside in the directory `/var/log/lights`. Therefore,
as part of your setup, you need to do the following:

.. code-block:: bash

  sudo mkdir /var/log/lights
  sudo chown lights:lights /var/log/lights

This allows processes owned by the `lights` meta-user to write all of the
logs in one place.

.. index::
   single: start HTTP server

Restart HTTP Server With New Configuration
------------------------------------------
By default, the `lighttpd` daemon will already be running. You need to
restart it to enable the new configuration with:

.. code-block:: bash

  sudo /etc/init.d/lighttpd restart

.. index::
   single: application server setup
   single: Flask
   single: flup
   single: WSGI

Application Server
==================
From this step forward, you should be logged in as user `lights`.

The HTTP server communicates with the outside world via HTTP on port 80,
but all of the program logic and UI implemtation is in a web app,
contained in a Python module.

That web app runs within
`Flask <https://palletsprojects.com/p/flask>`_. It also uses
`flup <https://www.saddi.com/software/flup/>`_ for its
`WSGI <https://wsgi.readthedocs.io>`_ implementation. The core Bardolph
code relies on
`lifxlan <https://pypi.org/project/lifxlan>`_. You  can install all these with:

.. code-block:: bash

  pip install Flask flup lifxlan

Because the Bardolph package lists `lifxlan` as a dependency, it may have
already been installed, in which case `pip` won't attempt to re-download it.

Start the Application Server
----------------------------
From the source distribution directory, for example ~/bardolph:

.. code-block:: bash

  ./start_fcgi

You should do this as the `lights` user.

If all goes well, you should be able to access the home page. Because
I've named my server "vanya" with raspi-config, I access it at
http://vanya.local.

For more information on using the web server, please see
:ref:`web_server`.

After a Reboot
--------------
Whenever you reboot the computer, you will need to start the FCGI process
again. To do so, `ssh` to the server as user `lights` and:

.. code-block:: bash

   cd bardolph
   ./start_fcgi

If you are clever enough with Linux, you can probably set up an init script
to do this. I'm investigatng this and will update these docs when it's ready.

By default, lighttpd is launched when the system boots, so you should not
need to manually start that process.

.. index::
   single: stop server

Stopping
========
To stop (and, if you want, start) the HTTP server:

.. code-block:: bash

  sudo /etc/init.d/lighttpd stop
  sudo /etc/init.d/lighttpd start


I don't have an elegant way to stop the FCGI process, so, as the `lights` user:

.. code-block:: bash

  killall python3

or

.. code-block:: bash

  killall python

.. index::
   single: web uninstall

Uninstalling
============
Uninstall with:

.. code-block:: bash

  pip uninstall bardolph

Aside from that un-install, you can also recursively delete the source tree.
