from config_base import ConfigurationBase

class ExtractKeywordsConfig(ConfigurationBase):
    def __init__(self, config_file):
        ConfigurationBase.__init__(self, config_file)
        self.processed_documents_folder = self.__getfilepath__("DEFAULT", "processed_documents_folder")
        self.file_mask                  = self.__getstring__("DEFAULT", "file_mask")

        self.min_document_frequency     = self.__getint__("DEFAULT", "min_document_frequency")
        self.max_phrase_length          = self.__getint__("DEFAULT", "max_phrase_length")
        self.max_proportion_documents   = self.__getfloat__("DEFAULT", "max_proportion_documents")

        self.stop_words_file            = self.__getstring__("DEFAULT", "stop_words_file")
        self.keywords_file              = self.__getstring__("DEFAULT", "keywords_file")