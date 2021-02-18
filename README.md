# TD Completes Me


![Repo Logo](/src/img/repo.PNG)


# What is this?
This is a combo TOX/Text Editor extension system that leverages TCP protocals to send a list of context sensitive auto-completion items to your Text Editor when editing externalDAT files for Derivitives Touch Designer




## What problem does this solve?
Creating extensive python scripts in Touch Designer can often be time consuming. We can use external editors like Sublime Text and VsCode but many of the features that make these tools beloved among traditional developers are not available to the Touch Designer programmer. This tool attempts to make editing the python scripts associated with Touch Designer projects a little more fluid and hopefully a little more joyful by implementing a (partial) autocompletion engine specific to the idioms of TD.

# Features

* ### `op('')` provides a list of operator names relative to the curent text DAT being edited


  ![OPS](/src/img/CHOP_720.gif)



 * ### get completions for CHOP channel names and DAT rows and cols!

 ![DAT](/src/img/DAT_720_still.png)

*  ### parameter auto completion. get a list of availabe parameters by typing `op('moviefilein1').par.`

![PAR](/src/img/PAR_720.png)

 * ### `self.ownerComp` is respected (as long as it's called `ownerComp`)
 ![PAR](/src/img/EXT_720.gif)
* ### completions for custom extension and TD provided operator methods and members
![MEMBER](/src/img/MEMBER.png)



## Requirments
Sublime Text 3 or MS VsCode

TD builds > 2020.20020

## Installation. 

# VsCode
Clone or download this REPO and then head over to the BUILDS directory. There you'll find a .vsix extension and a tox. You can install the vsix extension by hitting control+shift+P and selecting extensions=>install from vsix. You can also download the latest version from the Release Tab of the repo

# Sublime Text 3
Clone or download this REPO and head over to the subl directory. There you'll find a .sublime-package file as well as the source code for the Sublime Text Plugin. Install the package by placing it in the Installed Packages directory of Sublime. 


## Contributing
Feel free! We(meaning me) are actively accepting pull requests.


## Known Issues
Currently the `td_completes_me` uses a tcp based transport to communicate between Touch and VsCode/ST3. It will communicate by default on port 1338. If there is another process operating on this port then it will cause the extension to break. In practice this won't have any effect on editing your networks, you just won't get those sweet auto-completions!


## Tested On
PC. It will probably work on a Mac.

## Release Notes


### 0.3.0

Initial release.

### 0.3.1
fix warnings from external callback scripts





**Enjoy!**
