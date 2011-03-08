QPackage
========

When I fresh re-install my computer, I'm all the time googling a lot
to retrieve the name of the package I was missing.
I write all of them inside a .ini file and then I use my app to install them.

This app is only usable on debian-like operating systems (when apt is provided).
It's not intended to become an industrial software, but only to provide a few
functionalities.


Prelude
-------

pyqt4, distutils2 and python-apt are required::

    sudo apt-get install pyqt4-dev-tools python-apt python-setuptools
    sudo easy_install distutils2

Installation
------------

Download its tar.gz file (download link)::

    wget https://github.com/tonthon/packages/tarball/master
    tar -zxf packages.tar.gz

Build::

    cd packages/
    sudo make install

Then you can launch it::

    sudo qpackage

Installation rights are needed to launch the application (that's why we use sudo).

The inifile
-----------

A default inifile (mine) is provided.
Syntax::

    [section]
    packagename=packagedescription
