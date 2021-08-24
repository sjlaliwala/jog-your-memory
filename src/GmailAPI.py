import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from utils.DateUtil import reformat_date_string, date_string_to_date_time

class GmailAPI:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        self.service = self.generate_gmail_service()

    def generate_gmail_service(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('gmail', 'v1', credentials=creds)
        return service

    def get_messages_by_threads_by_contact_after_date(self, contacts_to_last_conversation_date):
        contacts_messages = {}

        for contact, last_conversation_date in contacts_to_last_conversation_date.items():
            search_query = self.construct_search_query(contact, last_conversation_date)

            threads = self.list_threads(search_query)
            contacts_messages[contact] = {}

            for thd in threads:
                thd_id = thd['id']
                messages = self.get_messages_from_thread(thd_id)
                contacts_messages[contact][thd_id] = messages

        return contacts_messages
        #TODO: CHANGE EVERYTHING TO FIT THIS FLOW, START HERE AND REFACTOR GMAIL.PY

    def construct_search_query(self, contact, after_date):
        return f'(to:({contact}) OR from:({contact})) After:{after_date}'

    def list_threads(self, search_query):
        try:
            results = self.service.users().threads().list(userId='me', q=search_query).execute()
            threads = results.get('threads', [])
            return threads
        except ValueError:
            print('Can\'t list threads')
            raise
        

    def get_messages_from_thread(self, thread_id):
        try:
            thread = self.service.users().threads().get(userId='me', id=thread_id).execute()
            messages = thread.get('messages', [])
            return messages
        except ValueError:
            print('Can\'t get thread')
            raise

    