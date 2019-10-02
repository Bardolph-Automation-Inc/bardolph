![bulb](bulb.png)
# Bardolph Web Server on Raspberry Pi

 Part of the [Bardolph Project](https://www.bardolph.org)

## Introduction
I originally wrote this application for my own use and have been using it
as my primary means of controlling my lights for about 4 months. Rather
than writing some kind of native app for my (Android) phone, I decided
that the best route would be to develop a browser-based UI.

A web-based app has these advantages:
1. Each script has a simple, dedicated URL. That allows me to put shortcuts
on my desktop and phone's home screen. For example, to turn on all the
lights, I unlock my phone, and tap the shortcut to the "all-off" web page.
This allows me to the lights on or off with one tap after I've unlocked my
phone.
1. After the bulbs boot up, there's no need for internet connectivity. Nobody
at Google or Amazon gets a record of when I turn my lights on and off.
1. I can acess the app from any browser in my apartment. For example, I
have a bookmark in my smart TV's web browser to the app, and I can
control my lights using my remote control.

To host the server, I wanted something cheap that wouldn't waste a lot of
power. The [Raspberry Pi Zero-W]
(https://www.raspberrypi.org/products/raspberry-pi-zero-w/) was an ideal fit.
Note, however, that other Raspberry Pi models with WiFi will work well. In
any case, the application won't put too much stress on the CPU.

## Preparation
The server runs an a basic installation of Raspbian. It also runs on Debian and
MacOS; basically, you need a Python interpreter version 3.5.1 or higher.

### O.S. Setup
This overview assumes you have already done the following, which are outside
the scope of this document:
1. Install Raspbian on your device. For more information, please refer to
the [Raspbian installation instructions]
(https://www.raspberrypi.org/documentation/installation).
1. Enable WiFi and ssh on your device. The server will run without a monitor
or keyboard attached. If you use a device with a physical ethernet port, you
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
sudo priveleges.

### Application Server
The Bardolph web UI runs within the 
[Flask framework](https://palletsprojects.com/p/flask/). You can install it
with:
```
% pip install Flask
```

### Web Server Setup
Because Bardolph runs as a WSGI application, multiple options exist for
hosting within a standalone container. In my particular case, I have aimed
for simplicity while avoiding commercial products (e.g. nginx) as much as 
possible. As a result, I've settled on lighttpd with FastCGI. Note that you
can use a different WSGI container and/or FastCGI integration. 

Installation of lighttpd is outside the scope of this document. I recommend
visting the [lighttpd website](https://www.lighttpd.net/) for more information.

The files included in the bardolph source tree under `web/server` are
apecific to lighttpd, but may be helpful for other containers. This just
happens to be how my own server at home is configured.

Note that these files assume that all of the logs, for both the Python app
and web server will go into the directory `/var/log/lights`. Therefore,
as part of your setup, you should do the following:
```
% sudo mkdir /var/log/lights
% sudo chown lights:lights /var/log/lights
```
This allows processes owned by the `lights` meta-user to write all of the
logs in one place.
