# Running the Software #

## Running `maestrod ` ##

`maestrod` is the server application for Maestro. In UNIX terminology, it runs as a daemon; in Windows terminology, it is a service. It must run with elevated privileges in order to do its job. This either means running `maestrod` as root, as the SYSTEM user (the under which Windows services are run), or as a Windows user with special permissions. More information is provided in the subsection below.

### Windows ###

To run `maestrod` on Windows without installing it as a service, the logged on user must be allowed to impersonate other users (which would normally be the logged on user unless s/he knows the passwords of other usrs). This is granted by modifying the security policies identified as "Impersonate a client after authentication" and "Replace a process level token" in the local security policies. (Modifying the security policy requires local administrator privilegs.) To change this security policy, follow these steps:

  1. open the Start Menu, click "Run..." and enter `secpol.msc` in the dialog box.
  1. Find the policy item labeled "Impersonate a client after authentication" and double-click it.
  1. In the dialog box, enter your user name (with domain if necessary) and click OK.
  1. Do the same for the policy item labeled "Replace a process level token."
  1. Log out and log in as the user who can now impersonate other users.

At that point, run the following at a console window prompt to start `maestrod` in debug mode:

```
> maestrod.py -debug
```

To install `maestrod` as a service rather than in debug mode, run the following (as a user with administrator privileges):

```
> maestrod.py --interactive install
> maestrod.py start
```

To stop the service later, run the following:

```
> maestrod.py stop
```

To remove the service, run the following:

```
> maestrod.py remove
```

### Linux/UNIX ###

Because `maestrod` uses PAM authentication by default (currently the only available option), the process must run as root in order to perform authentication. To test out `maestrod` as a non-daemon process, use the `su` command to become root and run `masestrod` with the `-debug` argument:

```
# ./maestrod.py -debug
```

## Running the Maestro GUI ##