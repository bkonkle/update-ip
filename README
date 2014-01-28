update-ip
=========

An extensible Python utility to automatically update your IP address with
dynamic DNS services, or notify you of such a change.  
Currently, we support the following services:

 - WebFaction
 - NearlyFreeSpeech
 
This utility was designed to be run
periodically through a scheduling utility like cron to keep your IP address
current.

Installation
------------


    $ pip install update-ip

Initial Setup
-------------

A configuration file is needed to store various options. This file can be 
created through a wizard, by running:

    $ update-ip -w

It will show you a list of available services, and ask 

 - where the configuration file should be kept
 - where the cache file should be kept (stores last known ip)
 - which domains do you want to update
 - the name of the service to run on IP change
 - service-dependent options
 
The domains should be separated by commas, with no spaces.


Normal Usage
------------

    $ update-ip /path/to/configuration/file

Automatic Domains
-----------------

If no domains are configured on the configuration file, the updater will 
only change the IPs of the domains that match the last known IP. This feature 
may not be available on all services.

Contributing
------------

Contributions to the project are greatly appreciated!  Please send pull
requests or patches, and we'll be glad to merge or apply them.

Development happens in [https://github.com/bkonkle/update-ip](https://github.com/bkonkle/update-ip)
