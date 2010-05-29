import xmlrpclib
from update_ip.services.base import BaseDNSService

class WebFactionService(BaseDNSService):
    name = 'Webfaction'
    
    def __init__(self, username, password):
        if not username or not password:
            raise AttributeError('Username and password are required for the '
                                 'Webfaction service.')
        self.server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
        self.session_id, self.account = self.server.login(username, password)
    
    def create(self, domain, ip):
        return self.server.create_dns_override(self.session_id, domain, ip)
    
    def read(self, domain):
        # Not doing this as a list comprehension because I only want to return
        # the first hit.
        for override in self.list_domains():
            if override['domain'] == domain:
                return override['a_ip']
    
    def update(self, domain, ip):
        self.delete(domain)
        return self.create(domain, ip)
    
    def delete(self, domain):
        return self.server.delete_dns_override(self.session_id, domain)
    
    def list_domains(self):
        return self.server.list_dns_overrides(self.session_id)
        
    def find_domains(self, ip):
        return [override['domain'] for override in self.list_domains()
                if override['a_ip'] == ip]

service = WebFactionService
