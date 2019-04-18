#!/usr/bin/env python

import feedparser
import os
import sys
import subprocess
import requests


FEED_URL = 'https://www.archlinux.org/feeds/news'
FEEDS_NUMBER = 3

SUMMARY = '{channel_title}'
BODY = '{title}\n\n\t{published}'

PACKAGES = [
    {
        'repo': 'community',
        'name': 'libfm-qt'
    },
    {
        'repo': 'community',
        'name': 'pcmanfm-qt'
    }
]

REPO_URL = 'https://www.archlinux.org/packages/{repo}/x86_64/{name}/json'
VERSION ='{pkgver}-{pkgrel}'


def _show_notification(summary, body, icon='help-info', urgency='normal', timeout=30000):
    if summary == None:
        summary = ''
    if body == None:
        body = ''

    subprocess.call(['notify-send', summary, body, '-i', icon, '-u', urgency, '-t', str(timeout)])


def read_feeds():
    feed = feedparser.parse(FEED_URL)
    title = feed['channel']['title']
    for i in feed['items'][:FEEDS_NUMBER]:
        _show_notification(
            SUMMARY.format(**i, channel_title=title),
            BODY.format(**i))


def get_repo_version(package):
    try:
        r = requests.get(REPO_URL.format(**package))
        if r.status_code == 200:
            return VERSION.format(**r.json())
        else:
            _show_notification('Not found in repo', package['name'], urgency='critical')
    except Exception as ex:
        _show_notification('Exception', ex.message, urgency='critical')
    return None


def get_local_version(package):
    try:
        process = subprocess.run(['pacman', '-Q', package['name']], capture_output=True, text=True)
        if process.returncode:
            _show_notification('Not found local', package['name'], urgency='critical')
        else:
            return process.stdout.split(' ')[1].strip()
    except:
        return None


def check_package_versions():
    for p in PACKAGES:
        r = get_repo_version(p)
        l = get_local_version(p)
        if r is not None and l is not None:
            if  r != l:
                _show_notification(p['name'], 'Needs upgrade\nLocal: %s\nRepo: %s' % (l, r), urgency='critical')
            else:
                _show_notification(p['name'], 'Up to date')


def main(argv):
    read_feeds()
    check_package_versions()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
