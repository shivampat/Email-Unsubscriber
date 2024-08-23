import base64
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage

SCOPES = ["https://mail.google.com/"]

def getService():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("gmail", "v1", credentials=creds)

def deleteUnreadEmails(service):
    
    nextPageToken = None
    
    while True:
        result = service.users().messages().list(
            userId='me',
            q='label:unread',
            pageToken=nextPageToken,
        ).execute()
        
        ids = []
        for message in result['messages']:
            ids.append(message['id'])
        
        service.users().messages().batchDelete(
            userId='me',
            body={
                'ids': ids
            },
        ).execute()
            
        if 'nextPageToken' not in result:
            break
        else:
            nextPageToken = result['nextPageToken']
            
def getUnsubscribeHeaders(service):
    nextPageToken = None
    unsubscribeHeaders = []
    
    while True:
        results = service.users().messages().list(
            userId='me',
            q='',
            pageToken=nextPageToken,
        ).execute()
        
        for result in results['messages']:
            message = service.users().messages().get(
                userId='me',
                id=result['id'],
            ).execute()
            for header in message['payload']['headers']:
                if header['name'] == 'List-Unsubscribe':
                    unsubscribeHeaders.append({
                        'id': result['id'],
                        'header': header['value'].split(',')
                        })
                    break
            
        if 'nextPageToken' not in result:
            break
        else:
            nextPageToken = result['nextPageToken']
    
    return unsubscribeHeaders

def emailUnsubscribeEmail(service, headers):
    for header in headers: 
        for link in header['header']:
            if link.find('mailto:') != -1:
                link = link.replace('<', '').replace('>', '')
                link = link.strip().split('?')
                
                email_to = None
                subject = None
                
                if len(link) == 2: 
                    mailto = link[0]
                    subjectUnformatted = link[1]
                    
                    email_to = mailto.replace('mailto:', '')
                    subject = subjectUnformatted.replace('subject=', '')
                else:
                    mailto = link[0]
                    email_to = mailto.replace('mailto:', '')
                
                print('Email: ', email_to, '\nSubject: ', subject)
                    
                message = EmailMessage()
                message['To'] = email_to
                message['From'] = service.users().getProfile(userId='me').execute()['emailAddress']
                message['Subject'] = subject
                
                encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

                create_message = {"raw": encoded_message}
                
                try:
                    send_message = (
                        service.users()
                        .messages()
                        .send(userId="me", body=create_message)
                        .execute()
                    )
                    print(f'Message Id: {send_message["id"]}')
                except:
                    print(email_to, ' failed.')
                    pass
                
def getUnsubscribeLinks(service, headers):
    links = []
    
    for header in headers: 
        for link in header['header']:
            if link.find('http') != -1:
                links.append(link.strip().replace('<', '').replace('>', ''))
    
    return links
                
                        
service = getService()
headers = getUnsubscribeHeaders(service)
# emailUnsubscribeEmail(service, headers)

links = set()
allLinks = getUnsubscribeLinks(service, headers)
for link in allLinks:
    links.add(link.strip().split("/")[2])\

print(links)