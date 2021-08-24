import pytextrank
import spacy

nlp = spacy.load("en_core_web_sm")
STOPWORDS = nlp.Defaults.stop_words
STOPWORDS |= {'nice', 'hope', 'let','know','best','regards','wishes','fond' 'regards','kind','looking','forward','hearing','regards','sincerely','thank','thanks','appreciation','cheers','faithfully','many','warmly','truly','love','ya','later','xoxo','thx','hugs'}
STOPWORDS |= {'srini', 'laliwala', 'matt', 'lara'}
nlp.add_pipe("textrank")

def get_top_phrases(messages):
    joined_messages = join_thread_messages(messages)
    text = remove_stopwords(joined_messages)
    top_phrases = rank_top_phrases(id, text)
    return top_phrases


def join_thread_messages(messages):
    joined_messages = ''.join(msg for msg in messages)
    return joined_messages

def rank_top_phrases(id, text):
    top_phrases = []
    text = remove_stopwords(text)
    doc = nlp(text)
    return doc._.phrases[:3]

    
              
def remove_stopwords(text):
    no_stopwords_words = []
    doc = nlp(text)
    for token in doc:
        if token.is_stop == False:
            no_stopwords_words.append(token.text)
    return ' '.join(no_stopwords_words)