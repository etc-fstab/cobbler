#!/bin/env python

# This is for python 3
"""
Query Oracle public page and look for latest OL 6-9 (x86_64) updates.
Send email to someone if find newer updates than ones from arguments input.
"""

import sys
import argparse
import requests
import re
from pkg_resources import parse_version
import bs4
import smtplib
from email.mime.text import MIMEText

mail_sender = "who-sends@your-domain.com"
mail_receiver = "who-receives@your-domain.com"
mail_server = "your-mail-server-fqdn-or-ip"

def email_new_update(body):
    """
    Send email about new update
    """
    message = MIMEText(body)
    message['Subject'] = f"{body}"
    fromaddr = mail_sender
    toaddr = mail_receiver
    try:
        email_object = smtplib.SMTP(host=mail_server)
        email_object.sendmail(fromaddr, toaddr, message.as_string())
    except SMTPException as err:
        sys.exit("SMTPException {0}" .format(err) + " Can't send email")

def get_web_page():
    """
    Get OL yum web page
    """
    url = "https://yum.oracle.com/oracle-linux-isos.html"
    page = requests.get(url)
    if page.status_code != 200:
        print(page.status_code)
        sys.exit("Status code is not 200")
    return page

def look_for_newer(page, r6u, r7u, r8u, r9u):
    """
    Look for newer OL updates.
    Argument are latest known updates for OL6-9
    """
    text = bs4.BeautifulSoup(page.text, 'html.parser')
    table = text.find('table')
    if table:
        column = table.find_all('strong')
        txt_column = [i.get_text() for i in column]
        # print(f"Available OL 6-9 updates: {txt_column}")
        ol9 = re.compile(r"^9")
        ol8 = re.compile(r"^8")
        ol7 = re.compile(r"^7")
        ol6 = re.compile(r"^6")
        for update in txt_column:
            if ol9.match(str(update)) and parse_version(update) > parse_version(r9u):
                # print(f"New OL9 update: {update}")
                email_new_update(f"New OL9 update is available: {update}")
            if ol8.match(str(update)) and parse_version(update) > parse_version(r8u):
                # print(f"New OL8 update: {update}")
                email_new_update(f"New OL8 update is available: {update}")
            if ol7.match(str(update)) and parse_version(update) > parse_version(r7u):
                # print(f"New OL7 update: {update}")
                email_new_update(f"New OL7 update is available: {update}")
            if ol6.match(update) and parse_version(update) > parse_version(r6u):
                # print(f"New OL6 update: {update}")
                email_new_update(f"New OL6 update is available: {update}")


def main():
    parser = argparse.ArgumentParser(description="Look for newer OL6-9 updates on yum.oracle.com.")
    parser.add_argument("--r6u", help="Latest known OL6 update", required=True)
    parser.add_argument("--r7u", help="Latest known OL7 update", required=True)
    parser.add_argument("--r8u", help="Latest known OL8 update", required=True)
    parser.add_argument("--r9u", help="Latest known OL9 update", required=True)
    args = parser.parse_args()
    r6u = args.r6u
    r7u = args.r7u
    r8u = args.r8u
    r9u = args.r9u
    page = get_web_page()
    look_for_newer(page, r6u, r7u, r8u, r9u)

if __name__ in '__main__':
    main()
