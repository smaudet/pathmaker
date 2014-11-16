pathmaker
=========

Easy cross-platform path editing

Download
========

Pre-built binaries are provided by Bintray:

http://dl.bintray.com/smaudet2/generic/pathmaker-setup.exe

Building
========

Install:

* Pywin32
* Pywin32ext
* Python 2.7 32 bit
* PyGTK 32 bit

Run:

`setup.py build`

To make the installer, install InnoSetup, double click the setup file, click 'run'. Install will be in ./Output/

Running
=======

Assuming you have the build depedencies listed above installed, simply run:

`pathmaker.py`


Why?
====

Because anyone who has ever used windows enviroment variables knows how much they suck. A couple issues are shown below:

 * Terrible Editor
 * Difficult to even 
 * No way to backup env settings
 * No way to quicky setup new settings
 * Issues with truncated values

Features
========

 * Full editing of system and user variables
 * Adding additional variables
 * Full, *resizable*, *scrollable* display.

Roadmap
=======

 * Delete support (50% complete)
 * Export support
 * Self contained exe (75% complete - installer generation and distutils in place)
 * Port to other platforms (linux/mac/android?)
