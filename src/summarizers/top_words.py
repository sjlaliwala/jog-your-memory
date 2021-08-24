import spacy
from collections import Counter
nlp = spacy.load('en_core_web_sm')

STOPWORDS = nlp.Defaults.stop_words
STOPWORDS |= {'nice', 'hope', 'let','know','best','regards','wishes','fond' 'regards','kind','looking','forward','hearing','regards','sincerely','thank','thanks','appreciation','cheers','faithfully','many','warmly','truly','love','ya','later','xoxo','thx','hugs'}
STOPWORDS |= {'srini', 'laliwala', 'matt', 'lara'}
def get_most_frequent_words(threads):
    thd_frequencies = {}
    for thd_id, messages in threads.items():

        frequency = {}
        all_messages = ''.join([msg['text'] for msg in messages])
        #print(all_messages)
        doc = nlp(all_messages.lower())
        # print(spacy.explain('dobj'))
        # for token in doc: 
        #     if (token.text == 'thought' or token.text == 'process'):
        #         print(token.text, '\t', token.lemma_, '\t', token.pos_,'\t', token.tag_,'\t', token.dep_,'\t', token.shape_,'\t', token.is_alpha,'\t', token.is_stop)
        words = [token.text for token in doc if not token.is_stop and not token.is_punct and (token.pos_ == 'NOUN' or token.pos_ == 'PROPN')]

        word_freq = Counter(words)
        print(word_freq)





#text = 'Hi Srini, Hope you had a nice weekend! Wanted to check in and make sure you received the online application and my email with our Tech Interest Survey. Do you have a better idea of when you’d like me to send out our online assessment? Let me know, Matt Lara Technical Recruiter | Worldwide Advertising View Amazon’s Leadership Principles here'
# text = 'Hope you had a nice weekend! Wanted to check in and make sure you received the online application and my email with our Tech Interest Survey. Do you have a better idea of when you\'d like me to send out our online assessment? Let me know, Would you mind sending the coding sample EOW? This week I am in the process of rotating to a new team as well, so next week I definitely will have time to complete it. Also, to confirm, I have received the coding sample and the tech interest survey. I\'ll send it your way Friday morning if that works. Let me know if anything changes in your schedule. Just to follow up here, I won\'t be able to send out the online assessment until you\'ve completed the application and technology interest survey. Let me know once that\'s taken care of and I\'ll send it out. Realized that I had not filled out the application. Should be submitted now, thanks for the reminder! Sounds good! Do you still want me to send the online assessment today? Friday works well! Sounds good, I\'ll send it your way Friday. I ran into an issue with your profile when I went to send you the online assessment. I\'m submitting a trouble ticket to get it resolved but it might take a day or so. I\'ll get you the OA as soon as possible but let me know if you have any questions or concerns. No problem at all!'



# doc = nlp(text.lower())

# words = [token.text for token in doc if not token.is_stop and not token.is_punct and (token.pos_ == 'NOUN' or token.pos_ == 'PROPN')]
# for token in doc: 
#     print(token.text, '\t', token.lemma_, '\t', token.pos_,'\t', token.tag_,'\t', token.dep_,'\t', token.shape_,'\t', token.is_alpha,'\t', token.is_stop)

# word_freq = Counter(words)

# print(word_freq)

