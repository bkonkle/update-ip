#!/usr/bin/env python
from __future__ import with_statement
import sys
import os
import urllib2
import socket
from datetime import datetime

from update_ip.services.webfaction import WebFactionService

class AlreadyRegisteredError(Exception):
    pass

class NotRegisteredError(Exception):
    pass

class InvalidServiceError(Exception):
    pass

class InvalidIPError(Exception):
    pass
    
# Global dict used by register. Maps custom services to callback classes.
registered_services = {}

def register(service):
    if service.name.lower in registered_services.keys():
        raise AlreadyRegisteredError('%s is already registered.' %
                                     service.name)
    registered_services[service.name.lower] = service

def unregister(service_name):
    if not service_name.lower in registered_services.keys():
        raise NotRegisteredError('%s is not registered.' % service_name)
    del registered_services[service_name.lower]

def get_service(service_name):
    if not service_name.lower in registered_services.keys():
        raise NotRegisteredError('%s is not registered.' % service_name)
    return registered_services[service_name.lower]

def get_list():
    """
    Returns a list of registered services.
    """
    return registered_services.keys()

def get_all():
    """
    Returns the registered_services dict.
    """
    return registered_services

# Register the built-in services
register(WebFactionService)

class IPUpdater(object):
    def __init__(self, service, ip_file=None, quiet=False):
        if not getattr(service, 'name'):
            raise InvalidServiceError('Please provide a valid service to use '
                                      'for updating the domains.')
        if not service.name in get_list():
            raise NotRegisteredError('%s is not registered.' % service.name)
        self.service = service
        self.ip_file = ip_file
        self.quiet = quiet
    
    def status_update(self, message):
        """
        If not silenced, print a status message prefixed by the current date
        and time.
        """
        now = datetime.now()
        now = now.strftime('%m/%d/%Y - %I:%M %p')
        if not self.quiet:
            print '%s: %s' % (now)
    
    def validate_ip(self, ip):
        """
        Use the socket library to validate the supplied IP. Return True if
        valid, False if not.
        """
        try:
            socket.inet_aton(ip)
        except socket.error:
            return False
        return True
    
    def check(self, prev_ip=None, return_new_ip=False):
        """
        Check to see if the current public IP has changed. Return true if
        changed, and False if not. Alternatively, if return_new_ip is passed
        as True, return the new public IP if changed.
        """
        if not prev_ip:
            if os.path.exists(self.ip_file):
                # Try to read the previous IP address
                with open(self.ip_file) as f:
                    prev_ip = f.read(f.read())
                    if not self.validate_ip(prev_ip):
                        sys.stderr.write('Invalid address found in %s' %
                                         self.ip_file)
                        sys.exit(1)
        
        # Get the public IP and compare it to the previous IP, if provided
        pub_ip = self.get_public_ip()
        if not self.validate_ip(pub_ip):
            raise InvalidIPError('Invalid address returned by IP service: %s'
                                 % pub_ip)
        if pub_ip == prev_ip:
            return False
        if return_new_ip:
            return pub_ip
        return True
    
    def get_public_ip(self):
        """Grab the current public IP."""
        pub_ip = urllib2.urlopen(
            "http://whatismyip.com/automation/n09230945.asp"
        )
        return pub_ip.read()
    
    def update(self, prev_ip=None, domains=None):
        """
        Check to see if the public IP address has changed. If so, update the
        IP for the requested domains on the selected DNS service. Send status
        update messages for use in logging.
        """
        pub_ip = self.check(prev_ip, return_new_ip=True)
        if pub_ip:
            self.status_update('Public IP has changed, updating %s.' %
                               self.service.name)
            
            # Update the ip_file
            with open(self.ip_file, 'w') as f:
                f.write(pub_ip)
            
            # If no specific domains were provided, use the service interface
            # to get all the domains whose current IP matches the previous
            # public IP.
            if not domains:
                domains = self.service.find_domains(prev_ip)
            
            for domain in domains:
                self.status_update('\tUpdating %s to %s.' % (domain, pub_ip))
                self.service.update(domain, pub_ip)
            
        self.status_update('Public IP has not changed.')
