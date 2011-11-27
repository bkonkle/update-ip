import re
import urllib2

class GetIpFailed(Exception):
    pass

ip_regex= re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

def get_ip_in_text( text ):
    ips= ip_regex.findall( text )
    if len(ips)==0:
        raise GetIpFailed("Could not get ip from text")
    if len(ips)>1:
        if ips.count(ips[0])!=len(ips): #if not all elements are equal
            raise GetIpFailed("Got multiple ips from text: "+str(ips))
    return ips[0]

def get_ip_from_http( url , change_user_agent=None):
    headers= {} if not change_user_agent else {'User-Agent':change_user_agent}
    request= urllib2.Request(url, headers=headers)
    try:
        page = urllib2.urlopen( request )
        text= page.read()
    except 'a':
        raise GetIpFailed("Error fetching page from url: "+url)
    return get_ip_in_text( text )

class BaseIpGetter(object):
    NAME = 'Base Ip Getter' # Replace this with the name of the IP getter
    def get_ip(self):
        raise NotImplementedError
