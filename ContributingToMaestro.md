# Contributing Code #

Once you have [checked out](GettingTheCode.md) the Maestro source code, you can fix bugs or implement features and then submit your changes as a ''patch'' for inclusion in Maestro.

Google Code Issues allow patch tracking in addition to bug and enhancement request tracking.  The [active issues](http://code.google.com/p/maestro/issues/list) report shows current bugs which need fixing as well as other users' enhancement requests. If you fix or implement one of these, your patch should be attached to the relevant ticket. If you fix a bug which is not listed, please create a ticket for your patch and attach the patch to that ticket.

Creating the patch once you've modified your code is easy.  From the Terminal, change to the opensg folder.  If it is in your home directory, this would be:

```
cd ~/maestro
```

and then type:

```
svn diff > myPatch.diff
```

where `myPatch` is a name for your patch. This will create a patch file which has only the changes you've made.

**NOTE**: If you have created new files, make sure to do the following for each added file _before_ running `svn diff`:

```
svn add Path/To/YourFileName
```

Please be sure your patch has been thoroughly tested and conforms to the coding style guidelines. It is recommended that you post to the [maestro-devel](http://groups.google.com/group/maestro-devel) group to notify the developers of the patch.