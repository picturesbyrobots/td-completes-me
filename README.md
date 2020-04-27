# TD Completes Me


![GitHub Logo](/src/img/repo.png)


# What is this?
This is an autocompletion engine extension and TOX that attempts to make writing python in TD a little easier


## Features

* Can't remember the name of that op you just dropped into the network? `td_completes_me` has you covered. 


* parameter auto completion is supported

* global operators

* `self.ownerComp` is respected (as long as it's called `ownerComp`)

* CHOP channels and DATS

* custom extension and baked in operator methods


## Requirments
Right now only VSCode is supported. If there's interest we'll consider a STL addon. 

TD builds > 2020.20020

## Installation. 
Header on over to the release page. There you'll find a .vsix extension and a tox. You can install the vsix extension by hitting control+shift+P and selecting extensions=>install from vsix.

you can also go here for feature breakdown and installation instructions.


## Known Issues
Currently `td_completes_me` will only work with one instance of Touch. In theory you could run two instances but because we use a TCP based transport running a second instance with a `td_completes_me` tox in it will cause things to BREAK

## Tested On
PC. It will probably work on a Mac.

## Release Notes

Users appreciate release notes as you update your extension.

### 1.0.0

Initial release of ...


**Enjoy!**
