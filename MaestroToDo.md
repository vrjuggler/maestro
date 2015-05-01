# Maestro To Do List #

Below are to-do items for Maestro development.

## Pending ##

### Unsorted ###

  * Create a test suite
  * Configuration editor enhancements
  * Application debug framework
    * Record all output from all nodes into a file(s)
    * Provide a method to submit debug information (E-MAIL)
  * Revisit the need for Process.py
  * Ensure that it is not possible to run two applications at the same time on a node.
    * We do need a way to run simple scripts while other apps are running. An example of this would be a script to clear the screensaver. This used to be called runSingleShotCommand, which was added on site at DMNS.
  * Decide how users should be able to extend Maestro
    * Currently we search through the modules directory loading all modules.
    * How should we decide the order to display these modules in the toolbar?
    * Is this directory going to explode in size? Should each modules have a subdirectory? `/path/to/maestro/modules/MyModule/`

## Completed ##

  * Decide on terminology
  * Add security
  * Create new artwork
    * Icons for each module
    * Splash screen image
  * Application configuration files