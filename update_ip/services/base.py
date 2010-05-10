class BaseDNSService(object):
    name = 'Service Name' # Replace this with the name of the DNS service
    
    def create(self, domain, ip):
        raise NotImplementedError
    
    def read(self, domain):
        raise NotImplementedError
    
    def update(self, domain, ip):
        raise NotImplementedError
    
    def delete(self, domain):
        raise NotImplementedError
    
    def find_domains(self, ip):
        raise NotImplementedError
