'''
email.py

prepare email message templates
'''

from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    ''' arguments: app, msg
    function sends msg
    '''
    with app.app_context():
        mail.send(msg)

def send_email(sent_to, subject, template, **kwargs):
    ''' arguments: sent_to, subject, template, kwargs
    thread to send async_email
    '''
    app = current_app._get_current_object()
    msg = Message(app.config['BRCREDIT_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['BRCREDIT_MAIL_SENDER'], recipients=[sent_to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
