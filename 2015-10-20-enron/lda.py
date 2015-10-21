import logging
import gensim
import cPickle as pkl


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

# load id->word mapping (the dictionary), one of the results of step 2 above
id2word = pkl.load(open('id2token.pkl'))
print(len(id2word))

# load corpus iterator
mm = gensim.corpora.MmCorpus('messages.mm')

# mm = gensim.corpora.MmCorpus(bz2.BZ2File('wiki_en_tfidf.mm.bz2')) # use this if you compressed the TFIDF output

N_TOPICS=4
print(mm)

lda = gensim.models.ldamodel.LdaModel(corpus=mm,
                                      id2word=id2word,
                                      num_topics=N_TOPICS,
                                      update_every=1,
                                      chunksize=mm.num_docs,
                                      passes=50)

lda.print_topics(N_TOPICS)
