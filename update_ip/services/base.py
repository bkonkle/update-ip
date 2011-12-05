class DNSServiceError(Exception):
    pass

class BaseDNSService(object):
    name = 'Service Name' # Replace this with the name of the DNS service

    def update(self, domain, ip):
        '''updates the domain with the new ip'''
        raise NotImplementedError
    
    def find_domains(self, ip):
        '''get all domains with the given ip'''
        raise NotImplementedError
