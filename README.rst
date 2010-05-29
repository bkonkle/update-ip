=========
update-ip
=========

An extensible Python utility to automatically update your IP address with
dynamic DNS services.  This initial release only supports WebFaction, but
other services will be coming soon.  This utility was designed to be run
periodically through a scheduling utility like cron to keep your IP address
current.

Installation
************

To install::

    pip install update-ip

Initial Setup
*************

A small text file is created to keep track of your current IP address.  Before
beginning regular use, update-ip needs to be run manually first with a list
of domain names to update the IP address for::

    $ update-ip -f /tmp/public_ip.txt -u myusername -p mypass \
    -d my.awesomedomain.com,even.coolerdomain.com webfaction

The filename is the name of the file that will be created and then read each
time the utility is run.  The username and password are for the dynamic DNS
service.  The domains should be separated by commas, with no spaces.  The
service name is the name of a module within update_ip/services/

    

