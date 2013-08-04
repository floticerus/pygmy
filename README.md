pygmy
======

a google play music library written in python and gtk3. although, it is more than likely switching to gtk2 for windows/osx compatibility.

this is not fully operational yet.

installation
======
right now this will only run on linux. there are two ways to run the program

------

there are no pre-built packages as of yet, so you'll need to build it with cxfreeze yourself

to run it with cxfreeze:
> `python setup.py build`

then, as root:
> `python setup.py install`

to run the program you would just type:
> `pygmy`

------

to run the python script directly, you will need:
- python2.7 (might work on older versions)
- gtk3
- gstreamer1.0
- [gmusicapi](https://github.com/simon-weber/Unofficial-Google-Music-API)
- glib
- pango

then just run:
> `python pygmy.py`