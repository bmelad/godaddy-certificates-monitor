import requests, json, base64, sys
from datetime import date, datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# GoDaddy Settings
shopperId = '{your-shopper-id}'
apiKey = '{your-api-key}'
apiSecret = '{your-api-secret}'
ignoreExpired = True # True or False
ignoreRevoked = True # True or False


# SMTP Settings
smtpServer = "{your-smtp-server-address}"
emailSender = "{email-address-of-the-report-sender}"
emailRecipients = "{comma-separated-list-of-email-recipients}"


def get_customer_id(key, secret, shopperId):
    headers = {'Authorization' : 'sso-key ' + key + ':' + secret}
    return requests.get('https://api.godaddy.com/v1/shoppers/' + shopperId + '?includes=customerId', headers = headers, verify = False).json()['customerId']

def list_certificates(key, secret, customerId):
    headers = {'Authorization' : 'sso-key ' + key + ':' + secret}
    return requests.get('https://api.godaddy.com/v2/customers/' + customerId + '/certificates', headers = headers, verify = False).json()['certificates']
    
def clean_date(date):
    return date[0:19].replace('T', ' ')
    
def calc_days_left(date):
    expiry_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return (expiry_date - datetime.now()).days
    
def send_email(sender, recipients, subject, content):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipients
    message.attach(MIMEText(content, "html"))
    with smtplib.SMTP(smtpServer) as smtp:
        smtp.sendmail(sender, recipients, message.as_string())

certificates = list_certificates(apiKey, apiSecret, get_customer_id(apiKey, apiSecret, shopperId))
html = """\
<!doctype HTML>
    <html>
        <head>
            <meta charset="utf-8" />
            <style type='text/css'>
                body { direction: ltl;  font-family:  Tahoma, Arial; font-size: 10pt; padding: 0px; background-color: #D7EFFA; text-align: center; }
                table { margin: auto; border: 1px dashed; }
                .header td { text-align: left; font-weight: bold; }
                td { padding: 10px;  text-align: left; }
                .alert td { color: #ff0000; }
                #written-by { text-align: center; padding: 3px; }
            </style>
        </head>
        <body>
            <h1>GoDaddy Certificates Report</h1>
            <h2>Weekly certificates report for """ + date.today().strftime("%d/%m/%Y") + """</h2>
            <table>
                <tr id="header"><td>Common Name</td><td>SAN</td><td>Status</td><td>Issue Date</td><td>Expire Date</td><td>Days Left</td></tr>
"""
for certificate in certificates:
    if ('status' in certificate and certificate['status'] != 'DENIED' and (not ignoreExpired or (ignoreExpired and certificate['status'] != 'EXPIRED')) and (not ignoreRevoked or (ignoreRevoked and certificate['status'] != 'REVOKED'))):
        sans = ''
        if ('subjectAlternativeNames' in certificate):
            sans = ', '.join(certificate['subjectAlternativeNames'])
        cls = 'ok'
        days_left = calc_days_left(clean_date(certificate['validEndAt']))
        if (days_left <= 60 or certificate['status'] == 'EXPIRED' or certificate['status'] == 'REVOKED'):
            cls = 'alert'
        html += '<tr class="' + cls + '"><td>' + certificate['commonName'] + '</td><td>' + sans + '</td><td>' + certificate['status'] + '</td><td>' + clean_date(certificate['validStartAt']) + '</td><td>' + clean_date(certificate['validEndAt']) + '</td><td>' + str(days_left) + '</td></tr>'
        #print(certificate['commonName'] + ', ' + certificate['status'] + ', ' + clean_date(certificate['validStartAt']) + ', ' + clean_date(certificate['validEndAt']) + ', ' + str(calc_days_left(clean_date(certificate['validEndAt']))))
        
html += """\
            </table>
            <div id="written-by">[ Elad Ben-Matityahu ]</div>
        </body>
    </html>
"""

send_email(emailSender, emailRecipients, "GoDaddy Certificates Report", html)

