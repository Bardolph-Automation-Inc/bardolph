# Bardolph Web Frontend Server
Al Fontes - [bardolph@fontes.org](mailto:bardolph@fontes.org)

![screenshot](web.png)
## Introduction
I originally wrote this application for my own use, and it serves
as my primary means of controlling my lights. However, it is designed to
*compliment* the LIFX mobile app, not to replace it.

In comparison to the LIFX mobile app, the local web server has these 
differences:
* Each script has its own URL. This makes it easy to access scripts with
bookmarks and a web browser.
* After the bulbs boot up, there's no need for external Internet connectivity.
* I can acess the app from any browser in my apartment, with none of the
hassles of logging in.

For example, to turn on or turn off off all the lights, I have have a couple
of home screen shortcuts on my phone. No need to navigate any mobile
app; after unlocking the phone, the lights are on or off with a single tap.
It's also  convenient to access the lights from my smart TV's web browser.

It's important to note that while this is a web server, it is not designed to
work on the public Internet. The server runs entirely within your WiFi
network. The target configuration is a very inexpensive device which
runs 24/7 as a headless server. At home I use a dedicated Raspberry Pi W
that sits in a corner of my apartment.

The server executes within the Flask framework. If you run it,
you should become familiar with Flask. In particular, you 
should follow their recommendations with respect to WSGI.

## Running the Server
The [Flask website](https://flask.palletsprojects.com) covers the general
topic of running a server, which falls outside the scope of this document. 
However, I can offer some specifics related to this particular application.

### Development Mode
You can run the server in so-called "development mode". Because the
server will run on a local network, the issues around security and
scalability are less of a concern. However, I would still recommend that
you run the server with some kind of a HTTP tier on port 80. Below you
can find instructions on configuring lighthttpd do fulfill that role.

For experimenting and development, you may just want to stick with
development mode. To start the server in that manner:
1. cd to the Bardolph home directory.
1. ``source web/setenv``
1. ``flask run``

The `setenv` script sets some environment variables used by Flask when
running the server.

By default, the logs are written to `/var/log/lights/lights.log`. On a Raspberry
Pi, I have a symbolic link from `/var/log/lights` to `/dev/shm`, so that the
log is written to the RAM drive.

On MacOS, I first create a RAM drive with this command:
```
diskutil erasevolume HFS+ rdisk `hdiutil attach -nomount ram://2048`
```
I then create a symbolic link from `/var/log/lights` to `/Volumes/rdisk`.

After you start the server, you can access it with:
http://localhost:5000.

### Manifest
The file `manifest.json` in the `scripts` directory contains the list of
scripts that should be available on the web site. That list also contains 
metadata for the scripts, mostly to control the appearance of their links. 

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

The manifest file contains standard JSON, as expected by the `json.load`
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
name of the script. It will replace any underscore or dash with a space, and
capitalize each word. For example, `reading.ls` yields "Reading", 
while `all-off.ls` yields "All Off".

The default for "path" is the base name of the file. In these examples, the URL's
would be http://localhost:5000/reading and http://localhost:5000/all-off.

The default for "repeat" is false.

### Usage
Clicking on a script button queues up the associated file containing that
script. Subsequent clicks append scripts to the back of the queue. As each
script finishes, the server executes the next in line.

Some scripts are run as repeatable: they are immediately started again when 
they have finished executing. Such scripts are designed to run continuously 
until stopped from the outside.

Aside from listing the scripts which are contained in the manifest the home page
also has some special-purpose buttons.

The "Stop" button immediately stops the current script and clears the queue of
any others. Because a script can potentially run indefinitely, you may need
this button if you want to access the lights immediately, or use an LIFX
app to control them. This button is the default mechanism for stopping a
repeatable script, which by design never stops.

The "Capture" button causes the server to query the lights and generate
a script that reflects their current settings. That file is
`scripts/__snapshot__.ls`. Clicking on "Retrieve" runs that script, thus
restoring the saved state.

Although the index page has no link to it, a page at http://server.local/status
lists the status of all the known lights in a very plain output with no CSS.

### LIFX Apps
Bardolph does nothing to directly interfere with the operation of the apps provided
by LIFX. However, a running script will continue to send commands to the bulbs.
Therefore, if you want to use the LIFX app or any other software, such as HomeKit
or Alexa, you should hit the "Stop" button on the Bardolph web site. Alternatively,
if you shut down the web server, that will also prevent Bardolph from sending any
more commands to the lights.

### "Production" Configuration
Although a so-called "production" configuration isn't necessary, I still recommend
it if you use a WSGI-enabled web frontend, as I do at home. This can be a complex
process, but I have provided some example configuration files in the source code
tree that may help. They can be found under `web/server`.

In my confguration, Flask provides a WSGI service. In a separate process,
[lighttpd]([https://https://www.lighttpd.net) attaches to that service through
FastCGI. Although the configuration files I have provided are intended to be
examples, I use them in their current state at home.

#### FastCGI Server - Raspbian
The first step is to run the Python code containing the web server within the
Flask framework. You can do this with the `start_fcgi_rpi` script in the
Bardolph directory. This is a simple script that launches `wsgi.py`, which in
turn starts Flask and the Bardolph web code.

The next step is to start the `lighttpd` daemon with the `start_server_rpi`
shell script. This is also very simple, doing little more than starting the process
with the appropiate configuration file.
