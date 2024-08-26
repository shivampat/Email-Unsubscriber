from flask import Flask, render_template, session, redirect, request, url_for, jsonify
import os, pathlib

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = 'email_secret_key'

client_secret = os.path.join(pathlib.Path(__file__).parent, 'client_secret.json')

REDIRECT_URI = 'https://localhost:5000/oauth2callback'
SCOPES = ["https://mail.google.com/"]
GOOGLE_CLIENT_ID = "809781650451-1ahm0omj06j57baq6qtcqt7h54ls0t95.apps.googleusercontent.com"

PRIVATE_KEY_FILE = os.path.join(pathlib.Path(__file__).parent, 'key.pem')
CERTIFICATE = os.path.join(pathlib.Path(__file__).parent, 'cert.pem')

def getService(cred_dict):
    credentials = Credentials(
        token=cred_dict['token'],
        refresh_token=cred_dict['refresh_token'],
        token_uri=cred_dict['token_uri'],
        client_id=cred_dict['client_id'],
        client_secret=cred_dict['client_secret'],
        scopes=cred_dict['scopes'],
    )
    
    return build("gmail", "v1", credentials=credentials)

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

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/get_links')
def get_links():
    service = getService(session['credentials'])
    headers = getUnsubscribeHeaders(service)
    return jsonify(headers)

@app.route('/login')
def login():
    flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secret,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    
    auth_url, state = flow.authorization_url()
    session['flow_state'] = state
    
    return redirect(auth_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/oauth2callback')
def oauth2callback():
    state = session['flow_state']
    flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secret,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state,
    )
    
    authorization_response = request.url
    flow.fetch_token(
        authorization_response=authorization_response,
    )
    
    credentials = flow.credentials
    session['credentials'] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token, 
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id, 
        "client_secret": credentials.client_secret, 
        "scopes": credentials.scopes,
    }
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(
        host='localhost', 
        debug=True, 
        ssl_context=('cert.pem', 'key.pem'),
        )