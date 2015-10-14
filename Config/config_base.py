import ConfigParser, os

class ConfigurationBase(object):

    def __init__(self, config_file):
        self.__cfg__ = self.__load_config_file__(config_file)
        pass

    def __load_config_file__(self, config_file):
        config = ConfigParser.ConfigParser()
        config.read([config_file])
        return config

    def __getstring__ (self, section, key):
        value = self.__cfg__.get(section, key)
        assert (value != None and value.strip() != "")
        return value

    def __getint__(self, section, key):
        value = self.__cfg__.getint(section, key)
        return value

    def __getbool__(self, section, key):
        value = self.__cfg__.getboolean(section, key)
        return value

    def __getfloat__(self, section, key):
        value = self.__cfg__.getfloat(section, key)
        return value

    def __getfilepath__(self, section, key):
        fname = self.__getstring__(section, key)
        assert os.path.exists(fname), "File path: %s does not exist" % fname
        return fname