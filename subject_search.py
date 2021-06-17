import os
import configparser
import imaplib
import email
from email.header import decode_header

# pull settings from the config file
config = configparser.ConfigParser()
config.read('config.ini')

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def findOrders():
    # login into email and get any unread messages
    mail = imaplib.IMAP4_SSL(config['EMAIL']['server'])
    mail.login(config['EMAIL']['user'], config['EMAIL']['pass'])
    mail.select("INBOX")
    _, search_data = mail.search(None, 'UNSEEN')
    
    for num in search_data[0].split():
        res, msg = mail.fetch(num, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()

                # check if subject is equal to orderSubject
                if subject == config['CONFIG']['order_subject']:
                    folder_name = "orders"
                    if not os.path.isdir(folder_name):
                        os.mkdir(folder_name)
                    filename = clean(msg["Date"]) + ".txt"
                    filepath = os.path.join(folder_name, filename)
                    with open(filepath, 'w') as f:
                        f.write(body)