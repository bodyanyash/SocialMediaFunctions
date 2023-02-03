from __future__ import print_function

import base64
import datetime
import json
import mimetypes
import os.path
import random
import time
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dateutil.parser
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']


def main(sender='', to='', subject='', message=''):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'): #Make as env variable or other secret import
        creds = Credentials.from_authorized_user_file('token.json', SCOPES) #Make as env variable or other secret import
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_id.json', SCOPES)  #Make env variable or import as other secret
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token: #Make as env variable or other secret import
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    message = create_message_with_attachment(sender, to, subject, message, '../logo.png')

    send_message(service, 'me', message)
    # Call the Gmail API
    '''results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])'''


def create_message_with_attachment(
        sender, to, subject, message_text, file):
    """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

  Returns:
    An object containing a base64url encoded email object.
  """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(file, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(file, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_message(service, user_id, message):
    """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def makeSubject(company='', followUp='0'):
    if followUp == '0':
        subject = f'{company} could use a hand with cybersecurity'
    else:
        subject = f'Is {company} a real company?'
    return subject

def makeMessage(company='', followUp='0'):
    if followUp == '0':
        message = f'     {company}, this message is for you. I am a licensed real estate broker in Illinois and cybersecurity professional. I understand the needs of client confidentiality and the restrictions on data processing... and the fines that come with noncompliance\n     Cybersecurity is a matter of "when" and not "if". Trawvid Sec creates fortune 500 level security frameworks that save you money in disasters and ongoing compliance. \nDo not waste money on templates and overpriced software. Most things can be solved for free nowadays and old software price gougers are panicking trying to scare you into buying their product. \n\n     Trawvid Sec has sifted through and tested software, frameworks, and network topologies so that we can bring you the best security without the giant price tag. A vulnerability management software could cost $10,000 a year or $0.00 a year if you have the right knowledge. Please do burn the budget on useless templates and overpriced garbage with makeup.\n\n     If you need compliance or simply do not want to run the risk of losing your entire business to ransomware or a hacker, please let me know. \nMy name is Nicholas DiVito, and I would be happy to discuss more of what we do. Thanks\n\nNicholas DiVito\nCyber Security Consultant\nTrawvid Sec LLC | https://www.trawvidsec.net\nCredly : https://www.credly.com/users/nicholas-divito/badges'
    else:
        message = '     Hey, \n\nJust following up. Did you get my last message?'
    return message

def sleepRandom():
    time.sleep(random.randrange(180, 600))


dataPath = '../EmailScraper/email_extraction/GeneralContractors.json'
with open(dataPath) as json_file:
    data = json.load(json_file)

print(data)
for j in range(len(data)):
    i = data[j]
    if i['sent'] == '0':
        company = i['name']
        subject = makeSubject(company)
        message = makeMessage(company,'0')
        for email in i['emails']:
            #sleepRandom()
            recipient = email
            main('noreply@trawvidsec.net', recipient, subject, message)
        data[j]['sent'] = '1'
        data[j]['dateSent'] = datetime.datetime.now().isoformat()
    elif i['followUp'] == '0' and (datetime.datetime.now() - dateutil.parser.parse(i['dateSent'])).seconds >= 15:
        company = i['name']
        subject = makeSubject(company, '1')
        message = makeMessage(company, '1')
        sleepRandom()
        for email in i['emails']:
            recipient = email
            main('noreply@trawvidsec.net', recipient, subject, message)
        data[j]['followUp'] = '1'
    else:
        pass

jsonString = json.dumps(data)
jsonFile = open(dataPath, "w")
jsonFile.write(jsonString)
jsonFile.close()