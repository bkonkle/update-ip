#!/usr/bin/env python

import sys
import os
import xmlrpclib
import urllib2
import ConfigParser
from datetime import datetime

def main(argv):
    dns_overrides = (
        'override.example.com',
        'another_override.example.com',
    )

    pub_ip = urllib2.urlopen("http://whatismyip.com/automation/n09230945.asp")
    pub_ip = pub_ip.read()

    config_loc = os.path.expanduser('~') + '/.adoleo/global.config'

    now = datetime.now()
    now = now.strftime('%m/%d/%Y - %I:%M %p')

    if os.path.exists(config_loc):
        config = ConfigParser.SafeConfigParser()
        config.read(config_loc)

        prev_ip = config.get('network', 'pub_ip')

        if pub_ip == prev_ip:
            print now + ": IP has not changed."

            sys.exit()
        else:
            print now + ": IP has changed - updating IP."

            config.set('network', 'pub_ip', pub_ip)

            configfile = open(config_loc, 'wb')
            config.write(configfile)

    else:
        print now + ": Creating new config file and updating IP."

        config = ConfigParser.SafeConfigParser()
        config.add_section('network')
        config.set('network', 'pub_ip', pub_ip)

        configfile = open(config_loc, 'wb')
        config.write(configfile)

    server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
    session_id, account = server.login('webfaction_username', 'password')

    for override in dns_overrides:
        server.delete_dns_override(session_id, override)
        server.create_dns_override(session_id, override, pub_ip)
        print '\tOverride for %s updated.' % override

if __name__ == '__main__':
    main(sys.argv[1:])