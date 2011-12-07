#!/usr/bin/env python
import sys
import os
import urllib2
from datetime import datetime

import logging

from update_ip import ip_getters, services
from ip_getters.base import GetIpFailed
from ip_getters.dyndns import DynDns
from ip_getters.whatismyip import WhatIsMyIp
from services.base import DNSServiceError

IP_GETTERS=[DynDns(), WhatIsMyIp()]

class UpdaterError(Exception):
    pass
class InvalidServiceError(UpdaterError):
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
        raise UpdaterError("None of the ip_getters returned a good ip")

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
    def __init__(self, service, ip_file=None):
        if not getattr(service, 'name', None):
            raise InvalidServiceError('Please provide a valid service to use '
                                      'for updating the domains.')
        self.service = service
        self.cache= IPCheckerCache(ip_file, IP_GETTERS)
        
        #setup logging
        self.log= logging.getLogger('update_ip.updater')
        formatter = logging.Formatter('%(asctime)s\t%(message)s')
        hdlr = logging.StreamHandler( sys.stdout )
        hdlr.setFormatter(formatter)
        self.log.addHandler(hdlr) 
        self.log.setLevel(logging.INFO)

    def clear(self):
        self.cache.clear()

    def automatic_domains(self):
        prev_ip= self.cache.current()
        if prev_ip is None:
            #Domains must be given if no ip_file is provided.
            raise UpdaterError('No previous IP was found, and no domain '
                            'names were provided. Automatic domain '
                            'detection only works with a valid previous '
                            'IP.')
        try:
            return self.service.find_domains( prev_ip )
        except NotImplementedError:
            #service doesn't support 
            raise UpdaterError('No domain names were provided, and '
                            "this service doesn't support the needed "
                            'checking for automatic domains to work')

    def update(self, domains=None):
        """
        Check to see if the public IP address has changed. If so, 
        update the IP for the requested domains on the selected DNS 
        service.
        """
        if domains is None:
            domains= self.automatic_domains()
        if not self.cache.has_changed():    #checks for new ip
            self.log.info('IP has not changed.')
            return
        else:
            curr_ip= self.cache.current()
            self.log.warning('IP has changed to {0}'.format(curr_ip))
            for domain in domains:
                self.log.info('\tUpdating {0}'.format(domain))
                try:
                    self.service.update(domain, curr_ip)
                except DNSServiceError as e:
                    self.log.error('\t\tfailed: '+str(e))
                    pass    #continue to next domain
