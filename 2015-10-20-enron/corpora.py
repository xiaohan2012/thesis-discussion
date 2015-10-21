import re
import codecs
import nltk
import logging

from nltk.stem.porter import PorterStemmer

from gensim import corpora

logger = logging.getLogger('CorpusEnron')

stemmer = PorterStemmer()


def load_items_by_line(path):
    with codecs.open(path, 'r', 'utf8') as f:
        items = set([l.strip()
                    for l in f])
    return items


class CorpusEnron(corpora.TextCorpus):
    stoplist = load_items_by_line('lemur-stopwords.txt')
    valid_token_regexp = re.compile('^[a-z]+$')
    
    def get_texts(self):
        """
        Parse documents from the .cor file provided in the constructor. Lowercase
        each document and ignore some stopwords.

        .cor format: one document per line, words separated by whitespace.
        """
        with codecs.open(self.input) as f:
            for i, doc in enumerate(f):
                # if i==10:
                #     break
                print(i)
                yield [
                    word for word in nltk.word_tokenize(doc.lower())
                    if (word not in CorpusEnron.stoplist and
                        CorpusEnron.valid_token_regexp.match(word) and
                        len(word) > 2)
                ]

    def __len__(self):
        """Define this so we can use `len(corpus)`"""
        if 'length' not in self.__dict__:
            logger.info("caching corpus size (calculating number of documents)")
            self.length = sum(1 for doc in self.get_texts())
        return self.length


if __name__ == "__main__":
    c = CorpusEnron('messages.txt')
    
    dictionary = corpora.Dictionary(c.get_texts())

    print(dictionary)
    dictionary.filter_extremes(no_below=2, no_above=0.2)
    print(dictionary)

    vectors = [dictionary.doc2bow(tokens) for tokens in c.get_texts()]
    corpora.MmCorpus.serialize('messages.mm', vectors)
    
    import cPickle as pkl
    id2token = {i: t
                for t, i in dictionary.token2id.items()}
    print(len(id2token))
    pkl.dump(id2token, open('id2token.pkl', 'w'))

    # corpora.MmCorpus.save_corpus('messages.mm', c)

    # id2token = {i: t
    #             for t, i in c.dictionary.token2id.items()}
    # import cPickle as pkl
    # pkl.dump(id2token, open('id2token.pkl', 'w'))
