import json
import urllib2

from update_ip.services.base import BaseDNSService, DNSServiceError


class CloudflareService(BaseDNSService):
    name = 'Cloudflare'
    api_url = 'https://api.cloudflare.com/client/v4/'

    def __init__(self, email, api_key, dns_type, **kwargs):
        """Init the Cloudflare class
        :param email: Cloudflare login email
        :param api_key: Cloudflare Global API Key
        :param domain: Domain to update
        :param dns_type: Domain type (A: for IPv4, AAAA: for IPv6...)
        """
        if not email or not api_key:
            raise DNSServiceError('Email and "Global API key" are required for use the Cloudflare service.')

        # Cloudflare data
        self.email = email
        self.api_key = api_key

        # Domain Data
        self.domain = None
        self.dns_record = None

        # DNS Type
        self.record_type = dns_type

        # Cloudflare internal data
        self.zone_id = None
        self.record_id = None

    def update(self, domain, ip):
        """Parse the given domain and extract the TLD
        :param domain: Domain (or subdomain) to update
        :param ip: IP address to update
        """
        self.__parse_domain(domain)
        self.__update_ip(ip)

    def find_domains(self, ip):
        """Not implemented, since in cloudflare you can have multiple domains, subdomains, dns-records ... it would
        not be safe to try to update them all
        :param ip: IP address to update
        """
        raise NotImplementedError

    def __parse_domain(self, domain):
        """Parse the given domain and extract the TLD
        :param domain: Full domain
        """
        self.domain = ".".join(domain.split(".")[-2:])  # Convert from "any.sub.domain.tld" to "domain.tld"
        self.dns_record = domain

    @staticmethod
    def __parse_result(self, data):
        """Parse the JSON result and return a dict/list with data
        :param data: JSON data to parse
        """
        return json.loads(data)

    def __update_ip(self, ip, second_try=False):
        """Update selected DNS record with provided IP
        :param ip: IP address to update
        :param second_try: If Record_ID is empty try to get it, if everything fails in a second attempt, we throw an
                            exception.
        """
        if self.record_id is None:
            if second_try:
                raise DNSServiceError(
                    'Record ID is empty, we tried to find it, but it was not possible'
                )
            self.__get_dns_record()
            self.__update_ip(ip, True)
            return

        request = self.__create_request(self.__update_url,
                                        json.dumps({'name': self.dns_record, 'type': self.record_type, 'content': ip})
                                        )

        request.get_method = lambda: 'PUT'
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        result = opener.open(request)
        # data = self.parse_result(result.read())

    def __get_zones(self):
        """Get the zone info for selected domain
        """
        data = self.__api_get_request(self.__zones_list_url)
        if len(data[u'result']) > 0:
            self.zone_id = data[u'result'][0][u'id']
        else:
            raise DNSServiceError('No info found for domain: ' + self.domain)

    def __get_dns_record(self, second_try=False):
        """Get the DNS Record info for selected sub-domain
        :param second_try: If Zone_ID is empty try to get it, if everything fails in a second attempt, we throw an
                            exception.
        """
        if self.zone_id is None:
            if second_try:
                raise DNSServiceError(
                    'Zone ID is empty, we tried to find it, but it was not possible'
                )
            self.__get_zones()
            self.__get_dns_record(True)
            return

        data = self.__api_get_request(self.__dns_list_url)

        if len(data[u'result']) > 0:
            self.record_id = data[u'result'][0][u'id']
        else:
            raise DNSServiceError(
                'No info found for DNS Record: "' + self.dns_record + '" with DNS type: "' + self.record_type + '"'
            )

    def __api_get_request(self, url):
        """Makes a GET request to API and return parsed JSON
        :param url: URL address
        """
        request = self.__create_request(url)
        return self.__parse_result(urllib2.urlopen(request))

    def __create_request(self, url, data=None):
        """Creates the HTTP request and add headers
        :param url: API URL with the petition.
        :param data: Request Data
        """
        if data is None:
            request = urllib2.Request(url)
        else:
            request = urllib2.Request(url, data)

        request = self.__add_url_headers(request)
        return request

    def __add_url_headers(self, request):
        """Add headers to petition with auth data and other needed headers"""
        request.add_header('Content-Type', 'application/json')
        request.add_header('X-Auth-Key', self.api_key)
        request.add_header('X-Auth-Email', self.email)
        return request

    @property
    def __zones_list_url(self):
        """Generate the URL for get the Zone List info"""
        return '{0}zones?name={1}'.format(self.api_url, self.domain)

    @property
    def __dns_list_url(self):
        """Generate the URL for get the DNS List info"""
        return '{0}zones/{1}/dns_records?name={2}&type={3}'.format(self.api_url, self.zone_id, self.dns_record,
                                                                   self.record_type)

    @property
    def __update_url(self):
        """Generate the URL for update the DNS Record"""
        return '{0}zones/{1}/dns_records/{2}'.format(self.api_url, self.zone_id, self.record_id)


service = CloudflareService
