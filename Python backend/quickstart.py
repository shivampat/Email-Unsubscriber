import os.path
import json
import base64
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]


# def getMessageBodyFromId(service, message_id):
#   serviceDump = service.messages().get(userId='me', id=message_id).execute()
#   encodedMessageParts = serviceDump['payload']['parts']
#   for part in 


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    # results = service.messages().list(userId="me").execute()
    messages = []
    result = service.users().messages().list(
      userId='me',
      pageToken=None, 
    ).execute()
    print(result['messages'])
    newresult = service.users().messages().get(
      userId='me', 
      id=result['messages'][4]['id'],
    ).execute()
    
    with open('test2.json', 'w') as f:
      json.dump(newresult, f)
    
    
    
    # nextPageToken = None
    # while True:
    #   result = service.users().messages().list(
    #     userId='me',
    #     pageToken=nextPageToken, 
    #   ).execute()
      
    #   for message in result['messages']:
    #     messagePayload = service.users().messages().get(
    #       userId='me',
    #       id=message['id'], 
    #     ).execute()
    #     messages.append(messagePayload)
      
    #   if 'nextPageToken' not in result:
    #     break
    #   else:
    #     nextPageToken = result['nextPageToken']
    
    # with open('messages.pkl', 'wb') as f:
    #   pickle.dump(messages, f)
    

    
    

    # while 'nextPageToken' in result:
    #   for message in result['messages']:
    #     messagePayload = service.users().messages().get(
    #       userId='me',
    #       id=message['id'], 
    #     ).execute()
    #     messages.append(messagePayload)
    #   print(len(messages))
    #   result = service.users().messages().list(
    #     userId='me',
    #     pageToken=result['nextPageToken'],
    #   )
    



        

    # if 'messages' in result:
    #   for message in result['messages']:
    #     messageId = message['id']
    #     service.users().messages().delete(
    #       userId='me',
    #       id=messageId,
    #     ).execute()


  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()