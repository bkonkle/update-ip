#!/usr/bin/env python
import sys
import os
import urllib2
import json
from datetime import datetime

import logging

from update_ip import ip_getters, services
import ip_getters
from ip_getters.base import GetIpFailed
from services.base import DNSServiceError

DATA_DIR= os.path.join(os.path.expanduser("~"), ".update_ip")

class UpdaterError(Exception):
    pass
class InvalidServiceError(UpdaterError):
    pass

class State(object):
    def __init__(self, state_filename): 
        self.filename= state_filename
        try:
            self._readFile()
        except:
            #file doesn't exist?
            #Not in the correct format?
            self.clear()

    def _readFile(self):
        f= open(self.filename, 'r')
        content= json.loads(f.read())
        self.last_ip= content['last_ip']
        self.domains_state= content['domains_state']
        f.close()

    def _writeFile(self):
        content= json.dumps( {'last_ip': self.last_ip, 'domains_state': self.domains_state} )
        f= open( self.filename, 'w')
        f.write( content )
        f.close()

    def _getNewIp(self):
        try:
            return ip_getters.get_ip()
        except GetIpFailed:
            raise UpdaterError("Could not get ip address")
        

    def has_changed(self):
        '''checks for new ip, stores it in state, returns boolean'''
        current_ip= self._getNewIp()
        if current_ip==self.last_ip:
            return False
        else:
            self.last_ip= current_ip
            self.domains_state={}
            self._writeFile()
            return True

    def current(self):
        '''returns currently cached ip'''
        return self.last_ip or None

    def clear(self):
        '''clears state'''
        self.last_ip=''
        self.domains_state= {}
        self._writeFile()
    
    def is_updated( self, domain ):
        try:
            return self.domains_state[domain]
        except KeyError:
            return False
    
    def set_updated_state( self, domain, state ):
        assert state in (False,True)
        self.domains_state[domain]=state
        self._writeFile()
    
    def get_unupdated_domains( self ):
        return [ d for d,s in self.domains_state.iteritems() if s==False]
        

class IPUpdater(object):
    def __init__(self, service, ip_file=None):
        if not getattr(service, 'name', None):
            raise InvalidServiceError('Please provide a valid service to use '
                                      'for updating the domains.')
        self.service = service
        self.state= State(ip_file)
        
        #setup logging
        self.log= logging.getLogger('update_ip.updater')
        formatter = logging.Formatter('%(asctime)s\t%(message)s')
        hdlr = logging.StreamHandler( sys.stdout )
        hdlr.setFormatter(formatter)
        self.log.addHandler(hdlr) 
        self.log.setLevel(logging.INFO)

    def clear(self):
        self.state.clear()

    def automatic_domains(self):
        prev_ip= self.state.current()
        if not prev_ip:
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

    def _update_domain( self, domain, ip ):
        self.log.info('\tUpdating {0} to {1}'.format(domain, ip))
        try:
            self.service.update(domain, ip)
            self.state.set_updated_state( domain, True )
        except DNSServiceError as e:
            self.log.error('\t\tfailed: '+str(e))
            self.state.set_updated_state( domain, False )
        
    def update(self, domains=None):
        """
        Check to see if the public IP address has changed. If so, 
        update the IP for the requested domains on the selected DNS 
        service.
        """
        unupdated= self.state.get_unupdated_domains()
        curr_ip= self.state.current()
        if unupdated and curr_ip:
            self.log.warning("Unupdated domains at start: "+str(unupdated))
            for domain in unupdated:
                self._update_domain(domain, curr_ip)
        if domains is None:
            domains= self.automatic_domains()
        if not self.state.has_changed():    #checks for new ip
            self.log.info('IP has not changed.')
            return
        curr_ip= self.state.current()
        self.log.warning('IP has changed to {0}'.format(curr_ip))
        for domain in domains:
            self._update_domain(domain, curr_ip)
