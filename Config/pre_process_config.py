from config_base import ConfigurationBase

class PreProcessConfig(ConfigurationBase):
    def __init__(self, config_file):
        ConfigurationBase.__init__(self, config_file)
        self.documents_folder                   = self.__getstring__("DEFAULT", "documents_folder")
        self.file_mask                          = self.__getstring__("DEFAULT", "file_mask")
        self.processed_documents_folder         = self.__getfilepath__("DEFAULT", "processed_documents_folder")

        self.empty_processed_documents_folder   = self.__getbool__("DEFAULT", "empty_processed_documents_folder")
        self.parse_html                         = self.__getbool__("DEFAULT", "parse_html")
        self.minimum_file_size_chars            = self.__getint__("DEFAULT", "minimum_file_size_chars")
