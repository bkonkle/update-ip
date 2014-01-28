import ConfigParser
import inspect
from update_ip.services import services_by_name

class InvalidConfigFile( Exception ):
    pass

class Configuration(object):
    SECTION= "update_ip"
    OPTIONS= ('cache_file', 'domains', 'service_name')
    OPTIONS_DESCRIPTIONS= ('File where to cache last ip', 'Domains (comma-separated)', 'Name of the updater service')
    REQUIRED_OPTIONS= OPTIONS[:2]
    def __init__(self, **kwargs):
        options= {}
        for k,v in kwargs.items():
            #read given options
            options[k]=v
        for k in set(Configuration.OPTIONS).difference(kwargs.keys()):
            #set options that were not given to None
            options[k]= None
        self.__dict__= options #expose options as instance attributes, i.e: configuration.domains
        
        if self.domains:
            self.domains= [x.strip() for x in self.domains.split(",")]


    def write_to_file(self, filename):
        '''writes this configuration to a config file'''
        config = ConfigParser.RawConfigParser()
        config.add_section( self.SECTION )
        for k,v in self.__dict__.items():
            if type(v)==list:
                v=",".join(v)
            if not v is None:
                config.set(self.SECTION , k, v)
        with open(filename, 'wb') as configfile:
            config.write(configfile)

    @staticmethod
    def read_from_file(filename):
        '''creates a Configuration from a config file'''
        try:
            config = ConfigParser.RawConfigParser()
            config.read(filename)
            file_options= dict( config.items( Configuration.SECTION ))
            return Configuration(**file_options)
        except ConfigParser.NoSectionError as e:
            raise InvalidConfigFile(
                "Failed to read configuration from '{0}': {1}".format(
                    filename, e))

def configurationWizard():
    def read_string( field_name, allow_empty= False ):
        while True:
            print field_name, ("[Required]" if not allow_empty else "")+":"
            x= raw_input()
            if x or allow_empty:
                return x or None
    print "Generating a new configuration file"
    print "Available services:"+"\n  "+"\n  ".join(services_by_name.keys())
    filename= read_string("Configuration filename to write")
    options={}
    for k, desc in zip( Configuration.OPTIONS, Configuration.OPTIONS_DESCRIPTIONS):
        required= k in Configuration.REQUIRED_OPTIONS
        v= read_string( "{0} ({1})".format(desc,k), allow_empty= not required)
        options[k]= v
    
    svc_name = options['service_name']
    try:
        service= services_by_name[svc_name]
    except KeyError:
        print "Sorry, '%s' is not a valid service name" % (svc_name)
        exit(3)
    
    print "Service parameters:"
    args, varargs, keywords, defaults= inspect.getargspec(service.__init__)
    for a in args:
        if a!='self':
            v= read_string( a, allow_empty= False)
            options[a]= v
        
    print "Generating and writing configuration to file: ", filename
    cfg= Configuration( **options )
    cfg.write_to_file(filename)
    print '''Finished. Please remember to set restrictive permissions \
if the file contains sensitive data (like a service password)''' 
