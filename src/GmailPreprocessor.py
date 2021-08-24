import base64
from bs4 import BeautifulSoup
import datetime
from time import sleep
from utils.SignatureParser import convert
import pytz
eastern = pytz.timezone('US/Eastern')
from utils.DateUtil import reformat_date_string, date_string_to_date_time

# If modifying these scopes, delete the file token.json.
class GmailPreprocessor:
    TO_DATE_FORMAT = '%Y/%m/%d'

    def __init__(self):
        pass

    def preprocess_messages(self, messages, last_conversation_date):
        preprocessed_messages = []
        for msg in reversed(messages):
            payload = msg['payload']

            gmail_created_date = self.get_gmail_created_date_header(payload)
            gmail_created_date = self.reformat_gmail_date_to_year_month_day(gmail_created_date)

            gmail_created_date_time = self.transform_date_string_to_date_time(gmail_created_date)
            last_conversation_date_time = self.transform_date_string_to_date_time(last_conversation_date)

            if self.is_gmail_created_date_before_last_conversation_date(gmail_created_date_time, last_conversation_date_time):
                return preprocessed_messages

            data = self.iteratively_get_data_from_payload(payload)

            if 'data' in data and data['size'] > 0:
                encoded_replaced_text = self.replace_encoded_gmail_characters(data['data'])
                decoded_text = self.base64_decode(encoded_replaced_text)
                decoded_text_less_email_signature = self.trim_email_excess(decoded_text)
                preprocessed_messages.append(decoded_text_less_email_signature)

        return preprocessed_messages

    def get_gmail_created_date_header(self, payload):
        created_date = None
        for header in payload['headers']:
            if header['name'] == 'Date':
                created_date = header['value']
                break
                    
        return created_date

    def reformat_gmail_date_to_year_month_day(self, gmail_header_created_date):
        if '(' in gmail_header_created_date:
            gmail_header_created_date = gmail_header_created_date.replace('(', '').replace(')', '')
            return reformat_date_string(gmail_header_created_date, '%a, %d %b %Y %H:%M:%S %z %Z', self.TO_DATE_FORMAT)
        
        else:
            return reformat_date_string(gmail_header_created_date, '%a, %d %b %Y %H:%M:%S %z', self.TO_DATE_FORMAT)
            
            

    def transform_date_string_to_date_time(self, date_string):
        return date_string_to_date_time(date_string, self.TO_DATE_FORMAT)

    def is_gmail_created_date_before_last_conversation_date(self, gmail_created_date_time, last_conversation_date_time):
        return gmail_created_date_time < last_conversation_date_time

    def iteratively_get_data_from_payload(self, payload):
        #TODO: FIGURE OUT HOW TO RECURSIVELY FIND THE TEXT OF AN EMAIL IN RESPONSE OR WHAT METHOD TO CALL
        while 'parts' in payload:
            payload = payload['parts'][0]

        return payload['body']

    def replace_encoded_gmail_characters(self, encoded_text):
        return encoded_text.replace("-","+").replace("_","/")

    def base64_decode(self, encoded_text):
        return base64.b64decode(encoded_text).decode('utf-8')
    

    def remove_greetings_and_endings(self, email):
        return convert(email)
        
    def trim_email_excess(self, text):
        email_without_past_thread = text.split('>', 1)[0]
        greeting_signature_trimmed_email = self.remove_greetings_and_endings(email_without_past_thread)
        return greeting_signature_trimmed_email


    def format_and_decode_messages(self, messages, after_date='1900/01/01'):
        """Generates a list of dictionaries that contain the subject, date of creation, and decoded message text of every message in a thread
        """
        decoded_messages = []
        #messages sorted in chronilogical order so have to reverse
        for msg in reversed(messages):
            payload = msg['payload']

            created_date = get_headers(payload)

            if created_date is None:
                MESSAGE_OUTCOME_LOG['no date'] += 1 
                continue
            
            try:
                reformatted_created_date = reformat_date_string(created_date, '%a, %d %b %Y %H:%M:%S %z', '%Y/%m/%d')
                # reformatted_date_created = reformat_date(date_created, '%a, %d %b %Y %H:%M:%S %z')
            except ValueError:
                created_date = date_created_string.replace('(', '').replace(')', '')
                reformatted_created_date = reformat_date_string(created_date, '%a, %d %b %Y %H:%M:%S %z %Z', '%Y/%m/%d')

            reformatted_created_date_time = date_string_to_datetime(reformatted_created_date, '%Y/%m/%d')
            after_date_time = date_string_to_datetime(after_date, '%Y/%m/%d')

            if reformatted_created_date_time < after_date_time:
                return decoded_messages

            else:
                #sometimes the body is split into doubly nested
                data = get_data_from_message(payload, MESSAGE_OUTCOME_LOG)

                if data is None or data['size'] <= 0:
                    print('skipping cause no data')
                    continue
                else:
                    data['data'] = data['data'].replace("-","+").replace("_","/")
                    decoded_data = trim_email_excess(base64.b64decode(data['data']).decode('utf-8'))
                    decoded_messages.append({'date': created_date, 'text': decoded_data})
        
        return decoded_messages

    