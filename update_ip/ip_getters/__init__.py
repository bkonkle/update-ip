import base
import getters
import logging
log= logging.getLogger('update_ip.ip_getters')

ALL_CLASSES= base.BaseIpGetter.__subclasses__()
ALL= [x() for x in ALL_CLASSES]

def get_ip():
    import random
    getters= ALL[:]
    random.shuffle( getters ) #for load balancing purposes
    for getter in getters:
        log.debug("Getting ip with getter {0}".format(getter.NAME))
        try:
            return getter.get_ip()
        except base.GetIpFailed as e:
            log.info("IpGetter {0} failed to get IP: {1}".format(getter.NAME, e))
    raise base.GetIpFailed("None of the ip_getters returned a good ip")
