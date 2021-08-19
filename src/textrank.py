import pytextrank
import spacy

nlp = spacy.load("en_core_web_sm")
STOPWORDS = nlp.Defaults.stop_words
STOPWORDS |= {'nice', 'hope', 'let','know','best','regards','wishes','fond' 'regards','kind','looking','forward','hearing','regards','sincerely','thank','thanks','appreciation','cheers','faithfully','many','warmly','truly','love','ya','later','xoxo','thx','hugs'}
STOPWORDS |= {'srini', 'laliwala', 'matt', 'lara'}
nlp.add_pipe("textrank")



def get_top_phrases(threads):
    for id, messages in threads.items():
        joined_messages = join_thread_messages(messages)
        rank_top_phrases(id, joined_messages)
        
        
        # print('next message')

def join_thread_messages(messages):
    joined_messages = ''.join(msg['text'] for msg in messages)
    return joined_messages

def remove_stopwords(text):
    no_stopwords_words = []
    doc = nlp(text)
    print(type(doc))
    for token in doc:
        if token.is_stop == False:
            no_stopwords_words.append(token.text)
    return ' '.join(no_stopwords_words)




def rank_top_phrases(id, text):
    text = remove_stopwords(text)
    doc = nlp(text)
    for phrase in doc._.phrases[:10]:
        print(phrase)
    print('next message')
        # print(phrase.text)
        # print(phrase.rank, phrase.count)
        # print(phrase.chunks)