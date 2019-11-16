.. index::
   web server; description

.. _web_server:

Web Frontend Server
###################
http://www.bardolph.org

.. :: web_mobile_small.png
   :align: center

I wrote this application for my own use, and it serves
as my primary means of controlling my lights. However, it is designed to
compliment the LIFX mobile app, not to replace it.

In comparison to a typical IoT installation, this local web server has
these  differences:

* Because each script has its own URL, I can easily launch a script with
  a browser bookmark.
* After the bulbs have booted up, there's no dependency on the Internet.
* I can acess the app from any browser in my apartment.
* Nobody at Amazon or Google knows when I turn my lights on.

For example, if you want to just turn off the lights, you may
find that navigating an app complicates a simple task. In my case,
I simply unlock the phone and turn off the lights off with a single 
tap on a home screen shortcut.

.. image:: home.png
   :align: center

It's also convenient to access the lights from my smart TV's web
browser. When I sit down to watch a movie, I don't have to find
my phone to dim the lights; I just use the TV.

.. image:: tv_screenshot.png
   :align: center

The target configuration for hosting the web site is a very inexpensive
device which runs 24/7 as a headless server. At home I use a dedicated
Raspberry Pi W that sits in a corner of my apartment.

.. figure:: server.jpg
   :align: center
   
   This is my server.

Running the Server
##################
The server executes within the 
`Flask framework <https://flask.palletsprojects.com>`_. If you run it,
you probably should become familiar with Flask.

Normally, you would want to run the web server in production mode,
with an HTTP server for the front end. Instructions for setting that
up are in :ref:`web_install`. However, if you're just experimenting,
the server can be run in development mode.

Development Mode
================
Because the server will run on a local network, the issues around
security and scalability are less of a concern.
For experimenting and development, you may just want to stick with
development mode. To do that, first:

.. code-block:: bash

  pip install Flask flup lifxlan

This installs the Python libraries that the Bardolph code relies on.

.. index::
   single: development server

Starting the Development Server
===============================
To start the server in that manner, cd to the root directory of the
source tree (ex: `~/bardolph`). Then:

.. code-block:: bash

  source web/setenv
  flask run


The `setenv` script sets some environment variables used by Flask when
running the server. After you start the server, you can access it with:
http://localhost:5000.

To stop the server,  press Ctrl-C.
  

.. index::
   single: manifest

Manifest
========
The UI is controlled by the contents of the manifest. Using the list of
scripts, the web app builds a list of colored boxes, each of which is
a link to URL that, when accessed, causes a script to be run.

The file `manifest.json` in the `scripts` directory specifies the list of
scripts that will be available on the web site. That list also contains 
metadata for the scripts, mostly to control the appearance of the web page. 

For example:

::

  // ...
  {  
    "file_name": "all_off.ls",
    "repeat": false,
    "path": "off",
    "title": "All Off",
    "background": "#222",
    "color": "Linen"
  },
  // ...


This snippet is used to launch the script "all-off.ls". Because "repeat" is
false, the script is run only once when you access the URL. 

The "path" setting determines the path on the web site that runs this script.
In this example, the manifest specifies that the URL
will be http://localhost:5000/off.

The string from "Title" appears in a colored box on the web page. That box
is is filled with the color specified by "background". The title is displayed
using the value from "color" for the text. In both cases, the strings for
colors derive from
`the CSS color space <https://developer.mozilla.org/Web/CSS/color_value>`_.
The strings are sanitized and passed through to the web page as a CSS class.

The manifest file contains standard JSON, as expected by the `json.load`
function in the Python standard library. The "repeat" value is optional,
and is assumed to be false if not present.

Default Behavior
================
For many scripts, default behaviors can be used to simplify the manifest:

::

  // ...
  {  
    "file_name": "reading.ls",
    "background": "#222",
    "color": "Linen"
  },
  // ...


If no value is supplied for "title", the server will generate it from the
name of the script. It will replace any underscore or dash with a space, and
capitalize each word. For example, `reading.ls` yields "Reading", 
while `all-off.ls` would yield "All Off".

The default for "path" is the base name of the file. In this example, the URL
would be http://localhost:5000/reading, and the script would not be repeated.

Usage
=====
Clicking on a script button queues up the associated file containing that
script. Subsequent clicks append scripts to the end of the queue. As each
script finishes, the server executes the next in line.

Some scripts are run as repeatable: they are immediately started again when 
they have finished executing. Such scripts are designed to run continuously 
until stopped from the outside.

Aside from listing the scripts which are contained in the manifest, the home page
also has some special-purpose buttons.

The "Stop" button immediately stops the current script and clears the queue of
all others. Because a script can potentially run indefinitely, you may need
this button if you want to access the lights immediately, or use an LIFX
app to control them. This button is the default mechanism for stopping a
repeatable script, which by design never stops.

The "Capture" button causes the server to query the lights and generate
a script that reflects their current settings. That file is
`scripts/__snapshot__.ls`. Clicking on "Retrieve" runs that script, thus
restoring the saved state.

Although the index page has no link to it, a page at http://server.local/status
lists the status of all the known lights in a very plain output with no CSS.

.. note::
  Clicking on a script appends it to the end of the queue. This means that
  you won't see anything happen if a lengthy script is already running. 
  When this happens, it's easy to conclude that the system is somehow not
  working. If you want to launch a script and have it start without waiting
  for the current one to finish, you should first click on the "Stop" link.

LIFX Apps
=========
Bardolph does nothing to directly interfere with the operation of the apps provided
by LIFX. However, a running script will continue to send commands to the bulbs.
Therefore, if you want to use the LIFX app or any other software, such as HomeKit
or Alexa, you should hit the "Stop" button on the Bardolph web site. Alternatively,
if you shut down the web server, that will also prevent it from sending any
more commands to the lights.

System Structure
################
This section gives a quick overview of the system architecture,
provided here for informational purposes.

The server stack has the following arrangement:

* The core Bardolph code that parses and runs scripts.
* An application server implemented in Python uses Flask to generate
  HTML pages. In the process of satisfying each page request, the server
  typically launches a lightbulb script.
* A WSGI layer, implemented by flup, which is part of the Python code.
  The Flask framework feeds generated web pages into this layer, which
  then makes them available via the WSGI protocol.
* A FastCGI (FCGI) process, created by spawn-fcgi, which connects to the
  WSGI layer and provides a FCGI interface. As part of its startup, spawn-fcgi
  launches the Python interpreter, runing the code for the Bardolph web server.
* An HTTP server, lighttpd, which is a separate process. It connects to the
  FCGI process and accepts connections over port 80. The HTTP server
  passes requests for web pages to the FCGI process, which gets the
  response from the Python code. While generating that response, the Python
  code will usually either launch or stop a lightbulb script.

That response is then passed up the chain to the user's browser.

HTTP Considerations
===================
You can use  a different WSGI container and/or FastCGI integration. 
For an example, see the integration with flup as implemented in
`wsgy.py`, in the root of the source distribution.

The files included in the bardolph source tree under `web/server` are
specific to lighttpd, but may be helpful for other containers. This just
happens to be how my own server at home is configured.
