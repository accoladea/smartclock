from flask_mail import Message
from smartclock import mail

def send_email2(to, subject, template):

	msg = Message(subject=subject,
	    recipients=[to],
	    html = template)
	mail.send(msg)

	return 'message is sent'