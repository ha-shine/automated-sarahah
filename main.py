import time
import json
import requests
import sendgrid
from sendgrid.helpers.mail import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

 # Sarahah link of the person you want to send the quote to 
 # eg. 'https://user123.sarahah.com/'
SARAHAH_URL = ''

# Link of the quotes api, currently using quotes.rest
QUOTE_API = 'https://quotes.rest/qod'

# Email Address of the recipient for notification emails
# eg. 'testuser@gmail.com'
NOTIFICATION_EMAIL = ''

# Sender of the notification emails
# eg. 'testuser@gmail.com'
SENDER_EMAIL = 'h@shine.rocks'

# Your sendgrid api key goes here
SENDGRID_API = ''

def send_email(sender, recipient, subject, message):
    client = sendgrid.SendGridAPIClient(apikey=SENDGRID_API)

    from_email = Email(sender)
    to_email = Email(recipient)
    content = Content('text/plain', message)

    mail = Mail(from_email=from_email, subject=subject, to_email=to_email, content=content)
    client.client.mail.send.post(request_body=mail.get())

def get_quote():
    try:
        r = requests.get(QUOTE_API)
        response = r.json()
        if 'success' in response:
            quote = response['contents']['quotes'][0]
            quote_body = quote['quote']
            quote_author = quote['author']
            return '%s - %s' % (quote_body, quote_author)
        else:
            raise Exception('QOTD fetched failure. No "success" element found in response')
    except Exception as e:
        handle_error(e)
        exit()

def send_qotd_to_sahara(quote):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(SARAHAH_URL)

        time.sleep(1)
        text_field = driver.find_element_by_id('Text')
        text_field.send_keys(quote)
        driver.find_element_by_id('Send').click()
        time.sleep(5)
        assert 'Thank you for your honesty' in driver.page_source
        driver.quit()
    except AssertionError:
        handle_error('"Thank you for your honesty" text not found in page_source')
        driver.quit()
        exit()
    except Exception as e:
        handle_error(e)
        driver.quit()
        exit()

def main():
    qotd = get_quote()
    send_qotd_to_sahara(qotd)
    handle_success(qotd)

def handle_success(quote):
    message = 'Successfully sent the following quote to %s.\n' % (SARAHAH_URL)
    message += '"%s"' % quote
    subject = 'Sarahah quote sent to %s' % SARAHAH_URL
    send_email(SENDER_EMAIL, NOTIFICATION_EMAIL, subject , message)

def handle_error(error):
    message = 'There is an error sending qotd to %s.\n' % (SARAHAH_URL)
    message += error
    subject = 'Sarahah error'
    send_email(SENDER_EMAIL, NOTIFICATION_EMAIL, subject , message)

if __name__ == '__main__':
    main()