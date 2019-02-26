from gensim.corpora.textcorpus import walk
from gensim.parsing.preprocessing import STOPWORDS as GENSIM_STOPWORDS
import os


class DirectoryCorpusConll(object):
    """A (nested) directory with files that contain each one document in Conll similar format.
       Each document is one line of tab-separated fields, each sentence is several lines followed
       by an empty line. The meaning of the tab-separated fields is variable, and which field
       gets used and how depends on the corpus initialisation."""

    def __init__(self, input, fieldindex=0, filterby=None, transform_sentence=None, extension=None):
        """Parameters: fieldindex: which field in each row do we want? stopwords: if None, use
        the gensim default stopwords, if [] use no stopwords, if a non-empty list, use those.
        filterby: a function that gets for each token a list of fields and returns the word or None.
        If this is specified, fieldindex is ignored.
        transform_fun: a function that takes a final gensim word list and produces a LIST of
        gensim wordlists. This can be used for multi-word substitution and other things."""
        self.fieldindex = fieldindex
        self.filterby = filterby
        self.input = input
        self.extension = extension
        self.transform_sentence = transform_sentence
        self.texts = 0
        self.files = 0
        self.original_tokens = 0
        self.filtered_tokens = 0
        self.final_tokens = 0
        self.min_depth = 0
        self.max_depth = 9999999999

    def iter_filepaths(self):
        for depth, dirpath, dirnames, filenames in walk(self.input):
            if self.min_depth <= depth <= self.max_depth:
                if self.extension is not None:
                    filenames = (n for n in filenames if n.endswith(self.extension))

                for name in filenames:
                    yield os.path.join(dirpath, name)

    def getstream(self):
        # this is responsible for reading in the corpus somehow and yielding "sentences", so this
        # code decides how to divide or merge files into what is seen as a document downstream.
        # Currently, one sentence from the file corresponds to one output sentence
        num_texts = 0
        num_files = 0
        for path in self.iter_filepaths():
            with open(path, 'rt') as f:
                # split at double newlines
                num_files += 1
                sents = f.read().rstrip().split("\n\n")
                for sent in sents:
                    num_texts += 1
                    yield sent
        self.texts = num_texts
        self.files = num_files

    def preprocess_text(self, text):
        # IN: text-the original "sentence" as somehow created by getstream from the input file(s)
        # OUT: returns a list of tokens for that document, tokenized, processed, filtered etc.

        # This is where self.character_filters, self.tokenizer and self.token_filters should also get
        # called. In our case we do not really have a use for them except token_filters

        # no need for character fileters, not doing this default behaviour
        # for character_filter in self.character_filters:
        #     text = character_filter(text)

        # the default tokeniser behaviour, not needed by us, we get the tokens out of the tsv column
        # tokens = self.tokenizer(text)
        # for token_filter in self.token_filters:
        #     tokens = token_filter(tokens)

        # we get a single set of rows of tokens for one sentence here, convert them into
        # a list of fields for the tsv
        token_tsvs = [f.split("\t") for f in text.split("\n")]
        self.original_tokens += len(token_tsvs)
        words = []
        for token_tsv in token_tsvs:   # a token_tsv is a single tsv row for that token
            if self.filterby:
                ret = self.filterby(token_tsv)   # return something from the whole tsv row
                if ret:                          # only add it if there is something
                    words.append(ret)
            else:
                words.append(token_tsv[self.fieldindex])
        self.filtered_tokens += len(words)
        if self.transform_sentence:
            ret = self.transform_sentence(words)
            self.final_tokens += sum([len(x) for x in ret])
            return ret
        else:
            self.final_tokens = self.filtered_tokens
            return [words]

    def __iter__(self):
        # getstream() returns the original file content. The sample_texts method uses this directly
        # instead of calling get_texts, and also passes the documents from getstream on to
        # proprocess_text. So we do most of the conversion in our own version of that method
        for doc in self.getstream():
            sents = self.preprocess_text(doc)   # this returns a list with one or more versions of the original sentence
            for tokens in sents:
                if tokens and len(tokens) > 1:
                    # print("DEBUG: yielding tokens=", tokens)
                    yield tokens

    def __len__(self):
        return self.texts

