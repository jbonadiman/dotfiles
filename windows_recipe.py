#!/usr/bin/env python3

import requests

import firefox


def sync_firefox_cookies() -> None:
    print('Syncing Firefox cookies exceptions...')

    print('Loading hosts...')
    resp = requests.get('https://pastebin.com/raw/FjKvjMzz')
    hosts = resp.text.split()

    print('Syncing...')
    firefox.sync_cookies(*hosts)
    print('Done!')


if __name__ == '__main__':
    try:
        sync_firefox_cookies()
    finally:
        pass
