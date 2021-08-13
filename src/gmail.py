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

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MONTH_TO_NUM = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

#DOW, D M (abrv) Y Time Millis -> Y/M/Day
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
    subject = None
    date_created = None
    for header in payload['headers']:
        if header['name'] == 'Subject':
            subject = header['value']
        elif header['name'] == 'Date':
            date_created = header['value'] 

        if date_created is not None and subject is not None:
            break
        
    return subject, date_created

def get_data_from_message(payload, counts):
    """Returns data (size and encoded text) from gmail response
    There are three different fromats where the data for an email message lies based on the size (how gmail splits things into parts)
    """
    data = None

    if 'parts' not in payload:
        data = payload['body']
        counts['payload[\'body\']'] += 1
    elif 'parts' not in payload['parts'][0]:
        data = payload['parts'][0]['body']
        counts['payload[\'parts\'][0][\'body\']'] += 1
    else:
        data = payload['parts'][0]['parts'][0]['body']
        counts['payload[\'parts\'][0][\'parts\'][0][\'body\']'] += 1
    
    return data


def make_message_list(service, thd_messages, counts, min_date='1900/01/01'):
    """Generates a list of dictionaries that contain the subject, date of creation, and decoded message text of every message in a thread
    """
    messages = []
    #messages sorted in chronilogical order so have to reverse
    for thd_msg in reversed(thd_messages):
        msg_id = thd_msg['id']
        
        msg = service.users().messages().get(userId='me', id=msg_id).execute()
        payload = msg['payload']

        subject, date_created = get_headers(payload)

        if date_created is None:
            counts['no date']+=1
            continue

        if reformat_date(date_created, '%a, %d %b %Y %H:%M:%S %z') < reformat_date(min_date):
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
                decoded_data = base64.b64decode(data['data']).decode('utf-8')
                messages.append({'date': date_created, 'subject': subject if subject is not None else '' , 'message': decoded_data})


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
    counts = {'no date': 0, 'date out of range': 0, 'skipped': 0, 'payload[\'body\']': 0, 'payload[\'parts\'][0][\'body\']': 0, 'payload[\'parts\'][0][\'parts\'][0][\'body\']': 0}

    for elem in threads:
        print(elem['id'])
        sleep(2)
        thd_id = elem['id']

        try:
            #Get a thread and all messages associated with it
            thd = service.users().threads().get(userId='me', id=thd_id).execute()
        except:
            print('Can\'t get thread')
        
        ovr += len(thd['messages'])
        #print(thd)
        thd_messages = make_message_list(service, thd['messages'], counts, min_date)

        messages_by_thd[thd_id] = thd_messages
        
    print('Overall message ids')
    print(ovr)
    print('Messages Added and Parts Breakdown')
    print(counts)

    return messages_by_thd  

def main():
    service = get_service()
    messages = get_emails_by_thread(service, 'laramate@amazon.com', '2021/07/21')
    
    # print(messages['17ae30d604b696f5'][0])
    # print()
    # print(messages['17ae30d604b696f5'][1])
    # print()
    # print(messages['17ae30d604b696f5'][2])
if __name__ == '__main__':
    main()