# Web Frontend Server

Part of the [Bardolph Project](http://www.bardolph.org)

![screenshot](web_mobile.png)
## Introduction
I originally wrote this application for my own use, and it serves
as my primary means of controlling my lights. However, it is designed to
compliment the LIFX mobile app, not to replace it.

In comparison to the LIFX mobile app, the local web server has these 
differences:
* Each script has its own URL. This makes it easy to access scripts with
bookmarks and a web browser.
* After the bulbs boot up, there's no need for external Internet connectivity.
* I can acess the app from any browser in my apartment without logging in
to anything.

For example, if you just want to turn off the lights, you may not
find that navigating an app is a bit too complicates. In my case,
to turn on or turn off off all the lights, I have have a couple
of home screen shortcuts on my phone. After unlocking the phone, 
the lights are on or off with a single tap.

It's also  convenient to access the lights from my smart TV's web
browser. When I sit down to watch a movie, I don't have to find
my phone to dim the lights; I just use the TV.

![home shortcuts on phone simultor](home.png)

It's important to note that while this is a web server, it is not designed to
work on the public Internet. The server runs entirely within your WiFi
network. The target configuration is a very inexpensive device which
runs 24/7 as a headless server. At home I use a dedicated Raspberry Pi W
that sits in a corner of my apartment.

## Running the Server
The server executes within the 
[Flask framework](https://flask.palletsprojects.com). If you run it,
you may want to become familiar with Flask.

### Development Mode
You can run the server in so-called "development mode". Because the
server will run on a local network, the issues around security and
scalability are less of a concern. However, I would still recommend that
you run the server with some kind of a HTTP tier on port 80. Below you
can find instructions on configuring lighthttpd do fulfill that role on
a Raspberry Pi.

For experimenting and development, you may just want to stick with
development mode. To do that, first:
```
pip3 install Flask flup lifxlan
```
This installs the Python libraries that the Bardolph code relies on.

### Log Configuration
By default, the logs are written to `/var/log/lights/lights.log`.
Therefore, you need a directory `/var/log/lights` which is writeable.

On MacOS, I first create a RAM drive with this command:
```
diskutil erasevolume HFS+ rdisk `hdiutil attach -nomount ram://2048`
```
I then create a symbolic link with:
```
sudo ln -s /var/log/lights` to `/Volumes/rdisk`.
```
On Raspberry Pi, there's already a ram disk, and the command is:
```
sudo ln -s /var/log/lights` to `/dev/shm`.
```

### Starting the Server
To start the server in that manner,  cd to the Bardolph
home directory. Then:
```
source web/setenv
flask run
```

The `setenv` script sets some environment variables used by Flask when
running the server. After you start the server, you can access it with:
http://localhost:5000.

To stop the server,  press Ctrl-C.

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
false, the script is run only once when you access the URL. 

The "path" setting determines the path on the web site that runs this script.
In this example, you would go to http://localhost:5000/off.

The string from "Title" appears in a colored box on the web page. That box
is is filled with the color specified by "background". The title is displayed
using the value from "color" for the text. In both cases, the strings for
colors correspond to CSS colors and are basically sanitized and passed
through to the web page.

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

### LIFX Apps
Bardolph does nothing to directly interfere with the operation of the apps provided
by LIFX. However, a running script will continue to send commands to the bulbs.
Therefore, if you want to use the LIFX app or any other software, such as HomeKit
or Alexa, you should hit the "Stop" button on the Bardolph web site. Alternatively,
if you shut down the web server, that will also prevent it from sending any
more commands to the lights.

## Hosting on Raspberry Pi
A key design goal for this project is to produce something that's
genuinely useful on an everyday basis. For me, that's a
local web server which is available 24/7. This means it
should be cheap to buy and consume a small amount of power.

The
[Raspberry Pi Zero-W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
has been a great fit. Other Raspberry Pi models will 
work as well, but the Zero-W is the cheapest, and is entirely powerful
enough for this purpose.

The server runs an a basic installation of Raspbian. It also runs on Debian and
MacOS; basically, you need a Python interpreter version 3.7 or higher.

#### O.S. Setup
This overview assumes you have already done the following, which are outside
the scope of this document:
1. Install Raspbian on your device. For more information, please refer to the
[Raspbian installation instructions](https://www.raspberrypi.org/documentation/installation).
1. Enable WiFi and ```ssh``` on your device. The server will run without a monitor
or keyboard attached. For more information, see the
[Raspberry Pi remote access documentation](https://www.raspberrypi.org/documentation/remote-access/ssh/).
 If your device has a physical ethernet port, you can use a wired
 connection, but the bulbs need to be on the same LAN.

By default, Raspbian already has a Python interpreter, so you won't need to
install it. However for more infirmation on running Python code,
please refer to the
[Raspberry Pi Python documentation](https://www.raspberrypi.org/documentation/usage/python).

### Dedicated User
A special-purpose user is convenient for running the server.
It provides you with a home directory for the Bardolph code, and allows
you to tailor that user's characteristics to running the server.
Therefore, the first steps are to create a user called `lights` and give it
sudo access.
```
adduser lights
sudo usermod -aG sudo lights
```
I also change the name of the server. In this example, my server will be
"stella", accessed on the command line and in my browser as
"stella.local". This can be done with
[raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md)

### Bardolph Distribution
To use the web server, you'll need the source distribution. You can
download it from https://github.com/al-fontes-jr/bardolph. If you
manually launch the web server, you must do so from the directory
containing the root of the project. Therefore, from the `/home/lights`
directory:
```
git clone https://github.com/al-fontes-jr/bardolph
```

### Application Server
The Bardolph web UI runs within the 
[Flask framework](https://palletsprojects.com/p/flask/). It also uses flup for
its WSGI implementation. The core Bardolph code relies on lifxlan. You 
can install all these with:
```
pip3 install Flask flup lifxlan
```
As of this writing, a default Raspbian distribution defaults to Python 2.7, 
hence the use of pip3 here. 

### HTTP Server Setup
Because Bardolph runs as a WSGI application, multiple options exist for
using a front-end to implement the HTTP protocol. I've settled on lighttpd,
which ships with a module for FastCGI.

Installation of lighttpd is outside the scope of this document. I recommend
visting the [lighttpd website](https://www.lighttpd.net/) for more information.
However, the basic installation can be done with:
```
sudo apt-get install lighttpd
```
This also installs `spawn-fcgi`.

To use the lighttpd configuration supplied in the source distribution,
you need create symbolic links to the root of the project, or copy the
congiguration files to `/etc/lighttpd`. I prefer symbolic links, because
the configuration files get updated automatically whenever you refresh
the source code from github.com.

For example, if you  downloaded the code from github to ~/bardolph:
```
cd /etc/lighttpd
sudo cp lighttpd.conf lighttpd.conf.original
sudo ln -s ~/bardolph/web/server/rpi/lighttpd.conf .
sudo ln -s ~/bardolph/web/server/common.conf .
```

### Logs Directory
The configuration files in the source distribution assume that all
of the logs, for both the Python app
and web server will go into the directory `/var/log/lights`. Therefore,
as part of your setup, you need to do the following:
```
sudo mkdir /var/log/lights
sudo chown lights:lights /var/log/lights
```
This allows processes owned by the `lights` meta-user to write all of the
logs in one place.

### Start and Stop the Server
To start the server, cd to the directory where you pulled down the source
from github.com. From there, you need to start two processes:
1. The web application server, a Python program that implements
the UI and runs the scripts, plus
1. The `lighttpd` process, which attaches to the Python app via FCGI and then
services incoming HTTP requests for web pages.

#### Start the Application Server
From the source distribution directory, for example ~/bardolph:
```
./start_fcgi
```

#### Start the HTTP server
By default, the `lighttpd` daemon will already be running. You can restart
it with:
```
sudo /etc/init.d/lighttpd restart
```
If all goes well, you should be able to access the home page. Because
I've named my server "stella" with raspi-config, I access it at
http://stella.local.

#### Stopping
To stop and start the HTTP server in separate steps:
```
sudo /etc/init.d/lighttpd stop
sudo /etc/init.d/lighttpd start
```
I don't have an elegant way to stop the FCGI process, so:
```
killall python3
```
or
```
killall python
```

## System Structure
This section gives a quick overview of the system architecture. It is
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

## HTTP Considerations
You can use  a different WSGI container and/or FastCGI integration. 
For an example, see the integration with flup as implemented in
```wsgy.py```, in the root of the source distribution.

The files included in the bardolph source tree under `web/server` are
specific to lighttpd, but may be helpful for other containers. This just
happens to be how my own server at home is configured.
