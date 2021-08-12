from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from bs4 import BeautifulSoup
import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MONTH_TO_NUM = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

#DOW, D M (abrv) Y Time Millis -> Y/M/Day
def reformat_date(date_str, from_format = None):
    print(date_str)
    print(type(date_str))
    if from_format is not None:
        date_str = datetime.datetime.strptime(date_str, from_format).strftime('%Y/%m/%d')
    date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
    # print(date)
    # print(type(date))
    #print(type(date))

    return date

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

def get_emails_to_and_from(service, contact, after_date):
    

    search_query = f'(to:({contact}) OR from:({contact})) After:{after_date}'
    #print(search_query)

    # Call the Gmail API


    results = service.users().threads().list(userId='me', q=search_query).execute()
    threads = results.get('threads', [])
    # print(threads)
    #messages = [{'id': '17b2c9aa38b3d7d8', 'threadId': '17ae30d604b696f5'}, {'id': '17b2c94f1971d0e1', 'threadId': '17ae30d604b696f5'}]

    messages = {}
    for elem in threads:
        messages[elem['id']] = []
        # print(msg['id'])
        try:
            thd = service.users().threads().get(userId='me', id=elem['id']).execute()
            #print(thd)
        except:
            print('Can\'t get thread')
        
        is_in_range = True
        i = 0
        for msg in reversed(thd['messages']):
            if not is_in_range:
                break
        
            date_created = None
            subject = None
            payload = msg['payload']
            for header in payload['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'Date':
                    i+=1
                    date_created = header['value'] 
                    #print(date_created)
                    #print(reformat_date(date_created))
                    #print(after_date)
                    
                if date_created is not None and subject is not None:
                    break
            #print(reformat_date(date_created) <= after_date)
            #print(type(reformat_date(date_created, '%a, %d %b %Y %H:%M:%S %z', '%Y/%m/%d'))); 
            #print(type(reformat_date(after_date, '%Y/%m/%d')))
            #print(reformat_date(date_created, '%a, %d %b %Y %H:%M:%S %z') <= reformat_date(after_date))
            if date_created is None:
                continue
            if reformat_date(date_created, '%a, %d %b %Y %H:%M:%S %z') < reformat_date(after_date):
                is_in_range = False
                continue
            else:
                if 'parts' not in payload['parts'][0]:
                    data = payload['body']
                else:
                    data = payload['parts'][0]['parts'][0]['body']
                #print(data)
                if data['size'] <= 0:
                    continue
                else:
                    data['data'] = data['data'].replace("-","+").replace("_","/")
                    decoded_data = base64.b64decode(data['data']).decode('utf-8')
                    messages[elem['id']].append({'date': date_created, 'subject': subject if subject is not None else '' , 'message': decoded_data})

    return messages    

def main():
    service = get_service()
    messages = get_emails_to_and_from(service, 'laramate@amazon.com', '2021/08/09')
    print(messages['17ae30d604b696f5'][0])
    print()
    print(messages['17ae30d604b696f5'][1])
    print()
    print(messages['17ae30d604b696f5'][2])
if __name__ == '__main__':
    main()