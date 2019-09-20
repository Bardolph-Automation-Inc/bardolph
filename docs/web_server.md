![bulb](../web/static/colorBulb-192.png) 
# Bardolph Web Frontend Server
Al Fontes - [bardolph@fontes.org](mailto:bardolph@fontes.org)

## Introduction
I originally wrote this application for my own use, and it serves
as my primary means of controlling my lights. However, it is designed to
*compliment* the LIFX mobile app, not to replace it.

It's important to note that while this is a web server, it is not designed to
work on the public Internet. The server runs entirely within your WiFi
network. The target configuration is a very inexpensive device which
runs 24/7 as a headless server. At home I use a dedicated Raspberry Pi W
that sits in a corner of my apartment.

In comparison to the LIFX mobile app, the local web server has these 
differences:
1. Each script has its own URL. This makes it easy to access scripts with
bookmarks and a web browser.
1. After the bulbs boot up, there's no need for external Internet connectivity.
1. I can acess the app from any browser in my apartment.

Currently, the web frontend is a thin layer that displays a simple
UI, with a back-end that queues up scripts present on the server's
file system. It has only one page, listing a set of available scripts. 

For example, to turning off all the  lights, I have a home screen shortcut on
my phone. No need to navigate any mobile app; after unlocking the phone, the
lights are off with a single tap. It's also convenient to access the lights
from my smart TV.

The server executes within the Flask framework. If you run it,
you should become familiar with Flask. In particular, you 
should follow their recommendations with respect to a reverse proxy.

## Starting the Server
I have used this process to run the server on my Mac, on a Raspberry Pi, 
and Debian Linux.

From the bash shell:
1. cd to the Bardolph home directory
1. ``source web/setenv``
1. ``start_server``

The `setenv` script sets some environment variables used by Flask and
Python when running the server.

The `start_server` shell script launches the server as a background task.
After you start it, you should be able to log off and let the server
run unattended. 

By default, the logs are written to `/var/log/lights/lights.log`. On a Raspberry
Pi, I have a symbolic link from `/var/log/lights` to `/dev/shm`, so that the
log is written to the RAM drive.

To shut down, run the `stop_server` shell script.

### Accessing the Server
If you run the web server on your own computer, you can access it with:
http://localhost:5000/lights. However, you will probably want to run it
on a standalone server. 

### Manifest
The file "manifest.json" in the "scripts" directory defines the content
of the web site. It contains a list of the scripts that should appear on the
web page. That list also contains metadata for the script, mostly to control
its appearance. 

For example:
```
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
```
This snippet is used to launch the script "all-off.ls". Because "repeat" is
false, the script is run only once. 

The "path" setting determines the path on the web site that runs this script.
In this example, you would go to (http://localhost:5000/off).

The string from "Title" appears in a colored box on the web page. That box
is is filled with the color specified by "background". The title is displayed
using the value from "color". In both cases, the strings for colors correspond
to CSS colors and are basically passed through to the web page.

The manifest file is a standard JSON file, as expected by the `json.load`
function in the Python standard library. The "repeat" value is optional,
and is assumed to be false if not present.

#### Default Behavior
For many scripts, default behaviors can be used to simplify the manifest:

```
// ...
{  
  "file_name": "reading.ls",
  "background": "#222",
  "color": "Linen"
},
// ...
```
If no value is supplied for "title", the server will generate it from the
name of the script. It will replace any underscore or dash with a space, and capitalize each word. For example, `reading.ls` yields "Reading", 
while `all-off.ls` yields "All Off".

The default for "path" is the base name of the file. In this example, it would
be http://localhost:5000/reading. The default for "repeat" is false.

### Usage
The web site lists all of the scripts which are contained in the manifest. It
also has some special-purpose buttons.

Clicking on a script button queues up the associated file containing that
script. Subsequent clicks append scripts to the back of the queue. As each
script finishes, the server executes the next in line.

Some scripts are run as repeatable: they are immediately started again when 
they have finished executing. Such scripts are designed to run continuously 
until stopped from the outside.

The "Stop" button immediately stops the current script and clears the queue of
any others. Because a script can potentially take hours to run, you may need
this button if you want to access the lights immediately. This button is also
the mechanism used to stop a repeatable script.

The "Capture" button causes the server to query the lights and generate
a script that reflects their current settings. That file is
`scripts/snapshot.ls`. Clicking on "Retrieve" runs that script, thus restoring
the saved settings.

