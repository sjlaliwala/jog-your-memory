from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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
    

    search_query = f'(to:({contact} OR from:({contact})) After:{after_date}'
    #print(search_query)

    # Call the Gmail API

    try:
        results = service.users().messages().list(userId='me', q=search_query).execute()
        messages = results.get('messages', [])
        print(messages)
        messages = [{'id': '17b2c9aa38b3d7d8', 'threadId': '17ae30d604b696f5'}, {'id': '17b2c94f1971d0e1', 'threadId': '17ae30d604b696f5'}]


        for msg in messages:
           # print(msg['id'])
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            #print(txt)
            #thread = service.users().threads().get(userId='me', id=msg.threadId).execute()
            try:
                payload = txt['payload']
                #print(payload)
                #tPayload = thread['payload']
                headers = payload['headers']
                #tHeaders = tPayload['headers']
                #print(payload)
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']

                #print(subject)
  
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.

                parts = payload.get('parts')[0]
                #print(parts)
                #print(parts)
                data = parts['parts'][0]['body']['data']
                #print(data)
                data = data.replace("-","+").replace("_","/")
                decoded_data = base64.b64decode(data).decode('utf-8')
                print(decoded_data)
                print('NEXT LINE')
            # # Now, the data obtained is in lxml. So, we will parse 
            # # it with BeautifulSoup library
            #     soup = BeautifulSoup(decoded_data, "html_parser")
            #     print(soup)
            #     body = soup.body()
            #     print(body)
  
            # # Printing the subject, sender's email and message
            #     print("Subject: ", subject)
            #     print("From: ", sender)
            #     print("Message: ", body)
            #     print('\n')
            except:
                pass
    except:
        print('cant')
def main():
    service = get_service()
    get_emails_to_and_from(service, 'laramate@amazon.com', '2021/08/09')

if __name__ == '__main__':
    main()