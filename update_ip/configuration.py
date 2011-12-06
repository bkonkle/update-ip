import ConfigParser

class Configuration(object):
    SECTION= "update_ip"
    OPTIONS= ('cache_file', 'service_name', 'domains', 'service_username', 'service_password')
    REQUIRED_OPTIONS= OPTIONS[:2]
    def __init__(self, **kwargs):
        options= {}
        for k,v in kwargs.items():
            #read given options
            if k in Configuration.OPTIONS:
                options[k]=v
            else:
                print "ignoring invalid option:",k,"=",v
        for k in Configuration.REQUIRED_OPTIONS:
            #validate all required options are present
            if not k in options:
                raise Exception("Missing mandatory option: "+k)
        self.__dict__= options #expose options as instance attributes, i.e: configuration.domains


    def write_to_file(self, filename):
        '''writes this configuration to a config file'''
        config = ConfigParser.RawConfigParser()
        config.add_section( self.SECTION )
        for k,v in self.__dict__.items():
            config.set(self.SECTION , k, v)
        with open(filename, 'wb') as configfile:
            config.write(configfile)

    @staticmethod
    def read_from_file(filename):
        '''creates a Configuration from a config file'''
        config = ConfigParser.RawConfigParser()
        config.read(filename)
        file_options= dict( config.items( Configuration.SECTION ))
        return Configuration(**file_options)
