from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from bs4 import BeautifulSoup
import datetime
from time import sleep
import spacy
from Parser import convert
import pytz
nlp = spacy.load('en_core_web_sm')
eastern = pytz.timezone('US/Eastern')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MONTH_TO_NUM = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}


def get_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

#DOW, D M (abrv) Y Time Millis -> Y/M/Day
def reformat_date(date_str, from_format = None):
    """Creates a date from the min_date in YYYY/MM/DD format
    Reformats date strings to YYYY/MM/DD if format argument is supplied
    Lists the user's Gmail labels.
    """
    if from_format is not None:
        date_str = datetime.datetime.strptime(date_str, from_format).strftime('%Y/%m/%d')
    date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
    return date
    
def get_headers(payload):
    """Gets necessary headers (subject and date of creation) from gmail message (from thread api) payload
    """
    date_created = None
    for header in payload['headers']:
        if header['name'] == 'Date':
            date_created = header['value']
            break
                
    return date_created

def get_data_from_message(payload, counts):
    """Returns data (size and encoded text) from gmail response
    Has to parse down 0 index of parts till it gets to the message
    """
    payload_str = 'payload'
    while 'parts' in payload:
        payload = payload['parts'][0]
        payload_str += '[parts][0]'


    key = payload_str + '[body]'
    
    if key not in counts:
        counts[key] = 1  
    else:
        counts[key] += 1

    return payload['body']
            
        
def remove_greetings_and_endings(email):
    return convert(email)
    
def trim_email_excess(text):
    """Previous messages linked from gmail thread exist in api call. They start at '<' in the text
    This returns only the message the id relates to without the rest of thread"""
    email_without_past_thread = text.split('>', 1)[0]
    greeting_signature_trimmed_email = remove_greetings_and_endings(email_without_past_thread)
    # print('COMPARE')
    # print(email_without_past_thread)
    # print("-----------------")
    # print(greeting_signature_trimmed_email)
    return greeting_signature_trimmed_email



def format_and_decode_messages(service, thd_messages, counts, min_date='1900/01/01'):
    """Generates a list of dictionaries that contain the subject, date of creation, and decoded message text of every message in a thread
    """
    messages = []
    #messages sorted in chronilogical order so have to reverse
    for msg in reversed(thd_messages):
        payload = msg['payload']

        date_created = get_headers(payload)

        if date_created is None:
            counts['no date'] += 1 
            continue
        
        try:
            reformatted_date_created = reformat_date(date_created, '%a, %d %b %Y %H:%M:%S %z')
        except ValueError:
            date_created = date_created.replace('(', '').replace(')', '')
            reformatted_date_created = reformat_date(date_created, '%a, %d %b %Y %H:%M:%S %z %Z')

        if reformatted_date_created < reformat_date(min_date):
            return messages

        else:
            #sometimes the body is split into doubly nested
            data = get_data_from_message(payload, counts)

            if data is None or data['size'] <= 0:
                counts['skipped'] += 1
                #print(payload)
                print('skipping cause no data')
                continue
            else:
                data['data'] = data['data'].replace("-","+").replace("_","/")
                #here is where the decoded data is

                decoded_data = trim_email_excess(base64.b64decode(data['data']).decode('utf-8'))
                messages.append({'date': date_created, 'text': decoded_data})
    return messages


def get_emails_by_thread(service, contact, min_date):
    """Generates a dictionary of lists for every thread and its messages
    """
    search_query = f'(to:({contact}) OR from:({contact})) After:{min_date}'
    #print(search_query)

    # List all gmail threads
    results = service.users().threads().list(userId='me', q=search_query).execute()
    threads = results.get('threads', [])
    # print(threads)
    #messages = [{'id': '17b2c9aa38b3d7d8', 'threadId': '17ae30d604b696f5'}, {'id': '17b2c94f1971d0e1', 'threadId': '17ae30d604b696f5'}]

    messages_by_thd = {}
    ovr = 0
    counts = {'skipped': 0, 'no date': 0}

    for elem in threads:
        print(elem['id'])
        thd_id = elem['id']

        try:
            #Get a thread and all messages associated with it
            thd = service.users().threads().get(userId='me', id=thd_id).execute()
        except:
            print('Can\'t get thread')
        
        ovr += len(thd['messages'])
        #print(thd)
        thd_messages = format_and_decode_messages(service, thd['messages'], counts, min_date)

        messages_by_thd[thd_id] = thd_messages
        
    print('Overall message ids')
    print(ovr)
    print('Messages Added and Parts Breakdown')
    print(counts)

    return messages_by_thd 

