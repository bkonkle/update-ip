#!/usr/bin/env python
import sys
import os
import urllib2
import socket
from datetime import datetime

class InvalidServiceError(Exception):
    pass

class InvalidIPError(Exception):
    pass

class IPUpdater(object):
    def __init__(self, service, ip_file=None, quiet=False):
        if not getattr(service, 'name', None):
            raise InvalidServiceError('Please provide a valid service to use '
                                      'for updating the domains.')
        self.service = service
        self.ip_file = ip_file
        self.quiet = quiet
    
    def update(self, domains=None, clear=False):
        """
        Check to see if the public IP address has changed. If so, update the
        IP for the requested domains on the selected DNS service. Send status
        update messages for use in logging.
        """
        if clear:
            self.clear_stored_ip()
        
        prev_ip = self.read_stored_ip()
        
        # If no previous IP is found, then automatic domain detection will
        # fail.  Domains must be given if no ip_file is provided.
        if not prev_ip and not domains:
            raise ValueError('No previous IP was found, and no domain '
                             'names were provided. Automatic domain '
                             'detection only works with a valid previous '
                             'IP.')
        
        # Get the public IP and compare it to the previous IP, if provided
        pub_ip = self.get_public_ip()
        if not self.validate_ip(pub_ip):
            raise InvalidIPError('Invalid address returned by IP service: %s'
                                 % pub_ip)
        if prev_ip and pub_ip == prev_ip:
            self.status_update('Public IP has not changed.')
            return
        else:
            self.status_update('Public IP has changed, updating %s.' %
                               self.service.name)
            
            # Update the ip_file
            f = open(self.ip_file, 'w')
            f.write(pub_ip)
            f.close()
            
            # If no specific domains were provided, use the service interface
            # to get all the domains whose current IP matches the previous
            # public IP.
            if not domains:
                domains = self.service.find_domains(prev_ip)
            
            for domain in domains:
                self.status_update('\tUpdating %s to %s.' % (domain, pub_ip))
                self.service.update(domain, pub_ip)
    
    def status_update(self, message):
        """
        If not silenced, print a status message prefixed by the current date
        and time.
        """
        now = datetime.now()
        now = now.strftime('%m/%d/%Y - %I:%M %p')
        if not self.quiet:
            print '%s: %s' % (now, message)
    
    def get_public_ip(self):
        """Grab the current public IP."""
        pub_ip = urllib2.urlopen(
            "http://whatismyip.com/automation/n09230945.asp"
        )
        return pub_ip.read()
    
    def read_stored_ip(self):
        if self.ip_file and os.path.exists(self.ip_file):
            # Try to read the previous IP address
            f = open(self.ip_file)
            prev_ip = f.read()
            f.close()
            
            if not self.validate_ip(prev_ip):
                raise InvalidIPError('Invalid address found in %s' %
                                     self.ip_file)
            return prev_ip
    
    def clear_stored_ip(self):
        if self.ip_file and os.path.exists(self.ip_file):
            # Remove the saved ip file
            self.status_update('Removing the currently stored IP address.')
            os.remove(self.ip_file)

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