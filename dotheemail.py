# Something in lines of http://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail
# Make sure you have IMAP enabled in your gmail settings.
# Right now it won't download same file name twice even if their contents are different.

import email
import uuid
import imaplib
import os, sys
import LogCheck2
from myconfig import *

detach_dir = '.'
if 'attachments' not in os.listdir(detach_dir):
    os.mkdir('attachments')

# userName = raw_input('Enter your GMail username:')
# passwd = getpass.getp ass('Enter your password: ')


try:
    imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
    typ, accountDetails = imapSession.login(gmail_user, gmail_password)
    if typ != 'OK':
        print('Not able to sign in!')
        raise

    imapSession.select('Inbox')
    typ, data = imapSession.search(None, '(UNSEEN)')
    if typ != 'OK':
        print('Error searching Inbox.')
        raise
    # Iterating over all emails
    newData = data[0].decode().split()
    for msgId in newData:
        typ, messageParts = imapSession.fetch(str(msgId), 'RFC822')
        emailBody = messageParts[0][1]
        mail = email.message_from_bytes(emailBody)
        for part in mail.walk():
            # print(part)
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            fileName = part.get_filename()
            if bool(fileName):
                tmpFileName = fileName.upper()
                if ".CSV" in tmpFileName:
                    saveAs = uuid.uuid4()
                    filePath = os.path.join(detach_dir, 'attachments', str(saveAs) + '.csv')
                    imapSession.uid('STORE', str(msgId), '+FLAGS', '\SEEN')
                    if not os.path.isfile(filePath):
                        print('CSV From: {0}, Saving CSV as: {1}'.format(mail['from'], filePath))
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                        logchk = LogCheck2.LogCheck(filePath, mail['from'])
                        logchk.ParseLog()

                        ##should probably add some logic to mark the message as unread if the attachment fails to download.
    imapSession.close()
    imapSession.logout()
except Exception as ex:
    # this block will catch ALL exception, not just imap.., messy difficult to troubleshoot,needs fixed.
    print('Not able to download all attachments. EXCEPTION: {0}'.format(ex))


#do emaily things here, download file, 
#logchk = LogCheck2.LogCheck( 'test.csv' ,  "bill.hatzer@gmail.com")
#logchk.ParseLog()

