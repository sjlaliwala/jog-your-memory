import math
from textblob import TextBlob as tb
import spacy
from collections import Counter
nlp = spacy.load('en_core_web_sm')
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')

STOPWORDS = nlp.Defaults.stop_words
STOPWORDS |= {'hey', 'hi', 'nice', 'hope', 'let','know','best','regards','wishes','fond' 'regards','kind','looking','forward','hearing','regards','sincerely','thank','thanks','appreciation','cheers','faithfully','many','warmly','truly','love','ya','later','xoxo','thx','hugs'}
STOPWORDS |= {'srini', 'laliwala', 'matt', 'lara'}

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

def remove_stopwords(text):
    text_tokens = nlp(text)
    tokens_without_sw = [token.text for token in text_tokens if not token.is_stop and not token.is_punct]
    return ' '.join(tokens_without_sw)

def generate_textblobs(messages):
    bloblist = []
    for msg in messages:
        filtered_msg = remove_stopwords(msg['text'].lower())
        bloblist.append(tb(filtered_msg))

    return bloblist


def get_most_important_words(threads):
    for thd, msgs in threads.items():
        print(thd)
        bloblist = generate_textblobs(msgs)
        for blob in bloblist:
            scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
            sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for word, score in sorted_words[:3]:
                
                print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))