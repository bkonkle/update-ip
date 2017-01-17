from update_ip.services.base import BaseDNSService, DNSServiceError

try:
    from pynfsn import pynfsn
except ImportError:
    raise Exception("This service requires the pynfsn package. You can find it on pypi or github")

import logging

log = logging.getLogger('update_ip.services.nfsn')

ALLOW_INEXISTENT = True  # If this is false, I'll refuse to proceed if the domain record doesn't already exist


def split_domain(domain):
    '''splits a complete domain into a pair of (subdomain, domain)'''
    s = domain.split(".")
    subdomain, domain = ".".join(s[:-2]), ".".join(s[-2:])
    return (subdomain, domain)


class NearlyFreeSpeechService(BaseDNSService):
    name = 'NearlyfreeSpeech'
    TTL = 300  # 5 minutes of dns record ttl

    def __init__(self, username, api_key, **kwargs):
        if not username or not api_key:
            raise DNSServiceError('Username and api_key are required for the '
                                  'NearlyFreeSpeech service.')
        self.nfsn = pynfsn.NFSN(username, api_key)

    def update(self, whole_domain, ip):
        subdomain, domain = split_domain(whole_domain)
        dns = self.nfsn.dns(domain)
        try:
            current_records = dns.listRRs(name=subdomain, type="A")
            current_records = filter(lambda x: x['name'] == subdomain, current_records)
        except Exception as e:
            raise DNSServiceError("failed to get current records: " + str(e))
        if len(current_records) > 1:
            raise DNSServiceError("Found more than one existing record with the given name: " + subdomain)
        inexistent = len(current_records) == 0
        if inexistent and not ALLOW_INEXISTENT:
            raise DNSServiceError("Found no existing record with the given name: " + subdomain)
        if inexistent:
            log.warning("domain " + whole_domain + " did not exist - creating it")
        else:
            record = current_records[0]
            if record.get("type") != "A":
                raise DNSServiceError('Not an "A" record')
            if record.get("name") != subdomain:
                raise DNSServiceError("Got a diferent record than expected")
            record_ip = record.get("data")
            # if record_ip==self.current_ip:
            #    #"Record already up to date."
            #    return
            try:
                dns.removeRR(name=subdomain, type=record.get("type"), data=record.get("data"))
            except Exception as e:
                raise DNSServiceError("failed to remove: " + str(e))
        try:
            dns.addRR(name=subdomain, type='A', data=ip, ttl=self.TTL)
        except Exception as e:
            raise DNSServiceError("failed to add: " + str(e))


service = NearlyFreeSpeechService
