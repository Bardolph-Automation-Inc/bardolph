![bulb](bulb.png)
# Bardolph Web Server on Raspberry Pi

 Part of the [Bardolph Project](https://www.bardolph.org)

## Introduction
One design goal for this project was to produce something that's
genuinely useful on an everyday basis. The resulting assumption is
that the web server described here is available 24/7. This means it
should be cheap to buy and consume a small amount of power.

The
[Raspberry Pi Zero-W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
has been a nice fit. Other Raspberry Pi models with WiFi will 
work as well. In any case, the application won't put too much stress on the 
CPU.

## Preparation
The server runs an a basic installation of Raspbian. It also runs on Debian and
MacOS; basically, you need a Python interpreter version 3.7 or higher.

### O.S. Setup
This overview assumes you have already done the following, which are outside
the scope of this document:
1. Install Raspbian on your device. For more information, please refer to
the [Raspbian installation instructions]
(https://www.raspberrypi.org/documentation/installation).
1. Enable WiFi and ```ssh``` on your device. The server will run without a monitor
or keyboard attached. If your device has a physical ethernet port, you
can use a wired connection, although the bulbs need to be on the same LAN.
For more information, see the [Raspberry Pi remote access documentation]
(https://www.raspberrypi.org/documentation/remote-access/ssh/).

By default, Raspbian already has a Python interpreter, so you won't need to
install it. However, you will need pip, so I recommend that you install it
as described in the [Raspberry Pi Python documentation]
(https://www.raspberrypi.org/documentation/usage/python).

### Dedicated User
I've found that a special-purpose user is convenient for running the server.
Therefore, the first steps are to create a user called `lights` and give it
sudo access.
```
adduser lights
sudo usermod -aG sudo lights
```
I also change the name of the server. In this example, my server will be
"stella", accessed on the command line and in my browser as
"stella.local". This can be done with [raspi-config]
(https://www.raspberrypi.org/documentation/configuration/raspi-config.md)

### Bardolph Distribution
To use the web server, you'll need the source distribution. You can
download it from https://github.com/al-fontes-jr/bardolph. If you
manually launch the web server, you must do so from the directory
containing the root of the project.
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
using a front-end to marshall HTTP requests. I've settled on lighttpd, which
ships with a module for FastCGI.

Installation of lighttpd is outside the scope of this document. I recommend
visting the [lighttpd website](https://www.lighttpd.net/) for more information.
However, the basic installation can be done with:
```
sudo apt-get install lighttpd
```
This also installs `spawn-fcgi`.

To use the configuration supplied in the source distribution, you need
create symbolic links to the root of the project. For example, if you 
downloaded the code from git to ~/bardolph:
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

### Start and Stop Server
To start the server, cd to the directory where you pulled down the source
from github.com. From there, you need to start two processes:
1. The web application server, a Python program that implements
the UI and runs the scripts, plus
1. The `lighttpd` process, which attaches to the Python app via FCGI and then
services incoming HTTP requests for web pages.

#### Start Application Server
From the source distribution directory, for example ~/bardolph:
```
./start_fcgi
```

#### Start HTTP server:
By default, the `lighttpd` daemon will already be running. You can restart
it with:
```
sudo /etc/init.d/lighttpd restart
```
If all goes well, you should be able to access the home page. Because
I've named my server "stella" with raspi-config, I access it at
http://stella.local.

#### Stopping
To stop and stgart the HTTP server in discrete steps:
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
The server stack has the following arrangement:
* Application server code implemented in Python uses Flask to generate
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
