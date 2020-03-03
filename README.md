![logo](https://www.bardolph.org/logo.png)
https://www.bardolph.org

# Bardolph Project

Al Fontes - [bardolph@fontes.org](mailto:bardolph@fontes.org)

**Bardolph** is a facility for controlling LIFX (https://www.lifx.com) lights
through a simple scripting language. It is targeted at people who would like
to control or experiment with their lights in an automated way, using a minimal
amount of coding.

Using their names, you can control individual lights, groups or locations. Or,
just pick a color for all the lights on your network. If you have any multi-zone
lights, the language allows you to set colors for specific zones.

The program does not use the Internet to access the bulbs, and no login is
required; all of its  communication occurs over the local WiFi network. You
can edit scripts with a basic text editor and run them from the command line.

The language may be missing some constructs you might expect, such as loops and
arithmetic expressons, as it's still under development. However, it is also
very simple, and should be usable by non-programmers.

## Quick Examples
Here is a script, named `all_on.ls`, that will turn on all your lights:
```
duration 1.5 on all
```
You run it with:
```
lsrun all_on.ls
```
In this case, `lsrun` is a bash shell script that become available after you
install Bardolph.

The `duration` parameter says to slowly shut off the
lights over a period of 1.5 seconds, which is a much nicer experience than
abruptly turning them off with no dimming.

Another example, `red.ls`, sets all the lights to a deep shade of red:
```
duration 1.5 hue 350 saturation 80 brightness 80 kelvin 2700
set all
```
To run it:
```
lsrun red.ls
```
The application executes in the foreground as long as a script is running. In this
example, the application will run for 5 minutes.

As a convenience, you can pass a script as a command-line parameter using
`lsrun -s`, followed by the script code in a quoted string. For example, to
turn off all the lights from the keyboard:

```
lsrun -s 'off all'
```

## Web Server
![web screenshot](https://www.bardolph.org/web_mobile.png)

The web server component makes scripts available in a user-friendly manner.
It implements a simple web page that lists available scripts and provides a
1:1 mapping betwen scripts and URL's. The server is designed to run locally,
on your WiFi network.

For example, if have a machine with the hostname
`myserver.local`, you could launch the  `all_on.ls` script by going to
`http://myserver.local/all-on` with any browser on your WiFi network.
Because scripts can run over a long period of time, even indefinitely,
a cheap, dedicated device like a Raspberry Pi is an ideal way to host the
web server.

## Python API
I've attempted to make it easy to use Bardolph scripts in your Python code.
For some uses, this may be significantly easier than learning and using a
full-purpose Python library. For example, here's a complete program that
waits 5 seconds, turns all the lights off, and turns them on again after
another 5 seconds:

```
from bardolph.controller import ls_module

ls_module.configure()
ls_module.queue_script('time 5 off all on all')
```

## System Requirements
The program has been tested on Python versions at or above 3.5.1. I
haven't tried it, but I'm almost certain that it won't run on any 2.x
version.

Because I haven't done any stress testing, I don't know the limits on
script size. Note that the application loads the encoded script into memory
before executing it.

I've run the program on MacOS 10.14.5 & 10.15, Debian Linux Stretch, and the
June, 2019, release of Raspbian. It works fine for me on a Raspberry Pi Zero W,
controlling 5 bulbs.

## Go Try It
For full documentation and download options, please see
[the main website](http://www.bardolph.org).
