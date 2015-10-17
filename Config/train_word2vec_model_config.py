from config_base import ConfigurationBase

class TrainWord2VecModelConfig(ConfigurationBase):

    def __init__(self, fname):
        ConfigurationBase.__init__(self, fname)

        self.keywords_files = self.__getstring__("DEFAULT", "keyword_files").split(",")

        self.processed_documents_folder = self.__getfilepath__("DEFAULT", "processed_documents_folder")
        self.stop_words_file = self.__getstring__("DEFAULT", "stop_words_file")
        self.file_mask = self.__getstring__("DEFAULT", "file_mask")
        self.min_sentence_length_words = self.__getint__("DEFAULT", "min_sentence_length_words")
        self.case_sensitive = self.__getbool__("DEFAULT", "case_sensitive")

        #Word2Vec training settings
        self.model_file = self.__getstring__("WORD2VEC", "word2vec_model_file")
        self.window_size = self.__getint__("WORD2VEC", "window_size")
        self.min_word_count = self.__getint__("WORD2VEC", "min_word_count")
        self.vector_size = self.__getint__("WORD2VEC", "vector_size")
        self.workers = self.__getint__("WORD2VEC", "workers")
        self.training_iterations = self.__getint__("WORD2VEC", "training_iterations")
        self.training_iterations = self.__getint__("WORD2VEC", "training_iterations")


