from GmailAPI import GmailAPI
from summarizers import textrank
from GmailPreprocessor import GmailPreprocessor
import datetime
#nmalik@andrew.cmu.edu
#laramate@amazon.com
#kanaklaliwala@yahoo.com
#salaliwala@gmail.com
#shrivats.12@gmail.com
#s13narayanan@gmail.com
def main():
    # date_str = 'Wed, 14 Apr 2021 15:58:47 -0400 (EDT)'
    # print(datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z'))
    contacts_to_last_conversation_date = {'s13narayan@gmail.com': '2020/05/05'}
    gmail = GmailAPI()
    contacts_threads_to_messages = gmail.get_messages_by_threads_by_contact_after_date(contacts_to_last_conversation_date) #'laramate@amazon.com',
    gmail_processor = GmailPreprocessor()
    
    contacts_threads_to_decoded_messages = {}
    for contact, threads in contacts_threads_to_messages.items():
        contacts_threads_to_decoded_messages[contact] = {}
        for thread_id, messages in threads.items():
            last_conversation_date = contacts_to_last_conversation_date[contact]
            preprocessed_messages = gmail_processor.preprocess_messages(messages, last_conversation_date)
            
            if len(preprocessed_messages) == 1 and preprocessed_messages[0] == '':
                continue

            contacts_threads_to_decoded_messages[contact][thread_id] = preprocessed_messages

     #print(contacts_threads_to_messages)
    ranked_phrases_per_thread_for_each_contact = {}
    for contact, threads in contacts_threads_to_decoded_messages.items():
        ranked_phrases_per_thread_for_each_contact[contact] = {}
        for thread_id, messages in threads.items():
            top_phrases = textrank.get_top_phrases(messages)
            ranked_phrases_per_thread_for_each_contact[contact][thread_id] = top_phrases
    
    print(ranked_phrases_per_thread_for_each_contact)
    
if __name__ == '__main__':
    main()