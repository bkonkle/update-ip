#!/usr/bin/env python
import sys
import os
import urllib2
from datetime import datetime

from update_ip import ip_getters
from ip_getters.base import GetIpFailed
from ip_getters.dyndns import DynDns
from ip_getters.whatismyip import WhatIsMyIp

IP_GETTERS=[DynDns(), WhatIsMyIp()]

class InvalidServiceError(Exception):
    pass

class IPCheckerCache(object):
    def __init__(self, cache_filename, getters):
        assert all( [isinstance(x, ip_getters.base.BaseIpGetter) for x in getters])
        self.getters= getters
        self.filename= cache_filename
        try:
            self._readFile()
        except:
            #file doesn't exist?
            self.clear()

    def _readFile(self):
        f= open(self.filename, 'r')
        self.last_ip= f.read()
        f.close()

    def _writeFile(self):
        f= open( self.filename, 'w')
        f.write( self.last_ip)
        f.close()

    def _getNewIp(self):
        for getter in self.getters:
            try:
                return getter.get_ip()
            except GetIpFailed:
                pass
        raise GetIpFailed("None of the ip_getters returned a good ip")

    def has_changed(self):
        '''checks for new ip, stores it in cache, returns boolean'''
        current_ip= self._getNewIp()
        if current_ip==self.last_ip:
            return False
        else:
            self.last_ip= current_ip
            self._writeFile()
            return True

    def current(self):
        '''returns currently cached ip'''
        return self.last_ip or None

    def clear(self):
        '''clears cache'''
        self.last_ip=''
        self._writeFile()

class IPUpdater(object):
    def __init__(self, service, ip_file=None, quiet=False):
        if not getattr(service, 'name', None):
            raise InvalidServiceError('Please provide a valid service to use '
                                      'for updating the domains.')
        self.service = service
        self.cache= IPCheckerCache(ip_file, IP_GETTERS)
        self.quiet = quiet
    
    def update(self, domains=None, clear=False):
        """
        Check to see if the public IP address has changed. If so, update the
        IP for the requested domains on the selected DNS service. Send status
        update messages for use in logging.
        """
        if clear:
            self.cache.clear()
        
        # If no previous IP is found, then automatic domain detection will
        # fail.  Domains must be given if no ip_file is provided.
        if self.cache.current is None and domains is None:
            raise ValueError('No previous IP was found, and no domain '
                             'names were provided. Automatic domain '
                             'detection only works with a valid previous '
                             'IP.')
        
        prev_ip= self.cache.current()
        if not self.cache.has_changed():    #checks for new ip
            self.status_update('Public IP has not changed.')
            return
        else:
            curr_ip= self.cache.current()
            self.status_update('Public IP has changed, updating %s.' %
                               self.service.name)

            
            # If no specific domains were provided, use the service interface
            # to get all the domains whose current IP matches the previous
            # public IP.
            if domains is None:
                domains = self.service.find_domains(prev_ip)
            
            for domain in domains:
                self.status_update('\tUpdating %s to %s.' % (domain, curr_ip))
                self.service.update(domain, curr_ip)
    
    def status_update(self, message):
        """
        If not silenced, print a status message prefixed by the current date
        and time.
        """
        now = datetime.now()
        now = now.strftime('%m/%d/%Y - %I:%M %p')
        if not self.quiet:
            print '%s: %s' % (now, message)
