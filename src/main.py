import gmail
import top_words as tw
import tfidf
import textrank
def main():
    threads = gmail.get_emails_by_thread(gmail.get_service(), 'nmalik@andrew.cmu.edu', '2021/03/03') #'laramate@amazon.com',
    textrank.get_top_phrases(threads)
    #tfidf.get_most_important_words(threads)
    #tw.get_most_frequent_words(threads)
    
    
    # print(messages['17ae30d604b696f5'][0])
    # print()
    # print(messages['17ae30d604b696f5'][1])
    # print()
    # print(messages['17ae30d604b696f5'][2])
if __name__ == '__main__':
    main()