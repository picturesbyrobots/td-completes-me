# TD Completes Me


![Repo Logo](/src/img/repo.PNG)


# What is this?
This is a combo TOX/VSCode extension that leverages the Language Server protocal to send a list of context sensitive auto-completion items to Microsofts Visual Studio code. 




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
 ![PAR](/src/img/ext_720.gif)
* ### completions for custom extension and TD provided operator methods and members
![MEMBER](/src/img/MEMBER.png)



## Requirments
Right now only VSCode is supported. If there's interest we'll consider a Sublime Text addon. 

TD builds > 2020.20020

## Installation. 
Clone or download this REPO and then head over to the BUILDS directory. There you'll find a .vsix extension and a tox. You can install the vsix extension by hitting control+shift+P and selecting extensions=>install from vsix. You can also download the latest version from the Release Tab of the repo


## Contributing
Feel free! We(meaning me) are actively accepting pull requests.


## Known Issues
Currently the `td_completes_me` uses a tcp based transport to communicate between Touch and VsCode. It will communicate by default on port 1338. If there is another process operating on this port then it will cause the extension to break. In practice this won't have any effect on editing your networks, you just won't get those sweet auto-completions!


## Tested On
PC. It will probably work on a Mac.

## Release Notes


### 1.0.0

Initial release.




**Enjoy!**
