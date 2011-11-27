from update_ip.services.base import BaseDNSService
try:
    from pynfsn import pynfsn
except ImportError:
    raise ImportError("This service requires the pynfsn package. You can find it on pypi or github")

def split_domain(domain):
    '''splits a complete domain into a pair of (subdomain, domain)'''
    s= domain.split(".")
    subdomain, domain= ".".join(s[:-2]), ".".join(s[-2:])
    return (subdomain, domain)
        
class NearlyFreeSpeechService(BaseDNSService):
    name = 'NearlyfreeSpeech'
    TTL= 300    #5 minutes of dns record ttl
    
    def __init__(self, username, api_key):
        if not username or not api_key:
            raise AttributeError('Username and api_key are required for the '
                                 'NearlyFreeSpeech service.')
        self.nfsn= pynfsn.NFSN(username, api_key)


    def update(self, domain, ip):
        subdomain, domain= split_domain(domain)
        dns= self.nfsn.dns( domain )
        
        current_records= dns.listRRs(name=subdomain, type="A")
        if len(current_records)>1:
            raise Exception("Found more than one existing record with the given name: "+subdomain)
        if len(current_records)==0:
            raise Exception("Found no existing record with the given name: "+subdomain)
        else:
            record= current_records[0]
            if record.get("type")!="A":
                raise Exception('Not an "A" record')
            if record.get("name")!=subdomain:
                raise Exception("Got a diferent record than expected")
            record_ip= record.get("data")
            #if record_ip==self.current_ip:
            #    #"Record already up to date."
            #    return
            dns.removeRR(name= subdomain, type=record.get("type"), data= record.get("data"))
            dns.addRR(name=subdomain, type='A', data=ip, ttl=self.TTL)


service = NearlyFreeSpeechService
