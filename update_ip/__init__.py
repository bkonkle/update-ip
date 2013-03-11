VERSION = '0.2'
IMPORTANT_INFO=25

import logging
log= logging.getLogger('update_ip')
log.setLevel(logging.DEBUG) #handlers handle filtering
logging.addLevelName(IMPORTANT_INFO, "IMPORTANT_INFO")

