.. image:: logo.png
   :align: center

.. index::
   single: installation; full instructions

.. _installation:

Installation
############
This page contains the full installation instructions, including setup
of the web server. Typically, initial installation takes one of two
forms:

#. Download and install the package.
#. Download the source, build the package, and install it.

Note that Python 3.5 or higher is required in all cases. **If your system
defaults to Python 2.x, you probably need to use
pip3 instead of pip.** Notable culprits here are Raspbian and Debian.

.. index::
   single: installation; package

Option 1: Built Package
=======================
This is the quickest way to get started. You won't necessarily have the
latest code, but that shouldn't be a problem. To do this kind of installation:

.. code-block:: bash

  pip install bardolph

After this intallation, the `lsc`, `lsrun`, and `lscap` commands will be
available in your `.local/bin` directory. In addition, if you're planning
on embedding scripts in your own Python program, the Bardolph support code
will be importable.

If you want to run the web server, you still need the source distribution:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph

This distribution also contains some sample scripts that can help you
get started.

.. index::
   single: building
   single: installation; local build
   
Option 2: Build and Install
===========================
This option allows you to modify source code, notably the configuration that's
built into the Python code. To do this, you need to have 
`setuptools <https://pypi.org/project/setuptools>`_ installed. If necessary:

.. code-block:: bash

  pip install setuptools 

With `setuptools` on your system:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph
  cd bardolph
  python setup.py bdist 
  pip install --no-index --find-links ./dist bardolph 

Note that the invocation of `setup.py` creates the `dist` directory. Within
that directory, it creates a `.whl` file containing the new package. When
you run `pip`, it finds that file and installs it.

When you get a newer release of the code, you can upgrade it with:
 
.. code-block:: bash

  python setup.py bdist 
  pip install --upgrade --no-index --find-links ./dist bardolph


Testing the Installation
========================
.. note:: The `lsrun`, `lscap`, and `lsc` commands are small Python
  programs that are installed in `.local/bin` in your home directory.
  Therefore, they are available only by typing in the full path name,
  such as:: 
        
    ~/.local/bin/lscap

  To make them available from any directory, I recommend adding the
  the following to your `.bash_profile` (or equivalent)::
    
     export PATH=~/.local/bin:${PATH}

  A more brute-force method is to use `sudo pip` when installing,
  which makes the commands available to every user with no changes
  to the path. However, that has a system-wide effect that you
  probably want to avoid. Another alternative is to use
  `virtualenv <https://virtualenv.pypa.io>`_.
   
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

.. index::
   single: uninstall

Uninstalling
============
Uninstall with:

.. code-block:: bash 

  pip uninstall bardolph

.. index::
   single: configuration
   single: logging configuration
   
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
will then read the file `config.ini` and replace whatever settings are overridden
by that file. For example, by default, all logging output is sent to the screen.
To override that setting and send output to a file, you could put the
following content into `config.ini`::

  [logger]
  log_file: /var/log/lights.log
  log_to_console: False

An example file with some candidates for customization are in the source
distribution, in the file `docs/bardolph.ini`. Note that this file is
for documentation purposes only; no configuration file outside of the
default Python code should be necessary.

.. index::
   single: web server; installation

Web Server Installation
#######################
These instructions focus on installing on a Raspberry Pi. However, they
should be fairly accurate for a typical Debian-based system.

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
connection instead of WiFi, but it needs to be on the same network
that the bulbs are on.

By default, Raspbian already has a Python interpreter, so you won't need to
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

  adduser lights

Note that this user doesn't have any special privileges, such as
being sudo'er. This ensures that the Python code itself is
run without any special access, thus improving security.

I also change the name of the server. In this example, my server will be
"vanya", accessed on the command line and in my browser as
"vanya.local". This can be done with
`raspi-config <https://www.raspberrypi.org/documentation/configuration/raspi-config.md>`_.

Bardolph Distribution
=====================
The first step is to do the installation as described at the top of
this doc. To run the web server, you'll need also the source distribution,
which contains the configuration files and templates for the Flask application.

Via `ssh`, log in to the Pi as user `lights`, and from the `/home/lights`
directory:

.. code-block:: bash

  git clone https://github.com/al-fontes-jr/bardolph

This will create a directory named `bardolph` and put the distribution
inside that directory.

.. index::
   single: application server setup
   single: Flask
   single: flup
   single: WSGI

Application Server
==================
The Bardolph web UI runs within 
`Flask <https://palletsprojects.com/p/flask>`_. It also uses 
`flup <https://www.saddi.com/software/flup>`_ for its
`WSGI <https://wsgi.readthedocs.io>`_ implementation. The core Bardolph
code relies on
`lifxlan <https://pypi.org/project/lifxlan>`_. You  can install all these with:

.. code-block:: bash

  pip install Flask flup lifxlan

As of this writing, a default Raspbian distribution defaults to Python 2.7, 
so you may need to `pip3` instead of `pip` throughout. Because the Bardolph
package lists `lifxlan` as a dependency, it may have already been installed,
in which case `pip` won't attempt to re-download it.

.. index::
   single: HTTP Server Setup
   single: lighttpd

HTTP Server Setup
=================
Because the Bardolph server runs as a
`WSGI <https://wsgi.readthedocs.io>`_ application, multiple options exist for
using a front-end to implement the HTTP protocol. I've settled on lighttpd,
which ships with a module for FastCGI.

Installation of lighttpd is outside the scope of this document. I recommend
visting the `lighttpd website <https://www.lighttpd.net>`_
for more information. However, the basic installation can be done with:

.. code-block:: bash

  sudo apt-get install lighttpd

This also installs `spawn-fcgi`. Of course, you will need to do this as
a user with `sudo` access, such as the default `pi` user.

To use the lighttpd configuration supplied in the source distribution,
you need create symbolic links to the root of the project, or copy the
congiguration files to `/etc/lighttpd`. I prefer symbolic links, because
the configuration files get updated automatically whenever you refresh
the source code from github.com.

For example, if you downloaded the code from github to `~lights/bardolph`:

.. code-block:: bash

  cd /etc/lighttpd
  sudo cp lighttpd.conf lighttpd.conf.original
  sudo ln -s /home/lights/bardolph/web/server/rpi/lighttpd.conf .
  sudo ln -s /home/lights/bardolph/web/server/common.conf .
  
Once again, you need to perform these steps while logged in as a user
with sudo access.

.. index::
   single: web logging configuration
   
Log Directory
=============
The web site configuration files in the source distribution specify
that all of the logs reside in the directory `/var/log/lights`. Therefore,
as part of your setup, you need to do the following:

.. code-block:: bash

  sudo mkdir /var/log/lights
  sudo chown lights:lights /var/log/lights

This allows processes owned by the `lights` meta-user to write all of the
logs in one place.

.. index::
   single: start server

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

You should do this as the `lights` user.

Start the HTTP Server
=====================
By default, the `lighttpd` daemon will already be running. You need to
restart it to enable the new configuration with:

.. code-block:: bash

  sudo /etc/init.d/lighttpd restart


If all goes well, you should be able to access the home page. Because
I've named my server "vanya" with raspi-config, I access it at
http://vanya.local.

.. index::
   single: stop server

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


Stopping
========
To stop (and, if you want, start) the HTTP server:

.. code-block:: bash

  sudo /etc/init.d/lighttpd stop
  sudo /etc/init.d/lighttpd start


I don't have an elegant way to stop the FCGI process, so:

.. code-block:: bash

  killall python3

or

.. code-block:: bash

  killall python
