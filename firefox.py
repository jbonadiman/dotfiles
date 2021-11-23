#!/usr/bin/env python3

import sqlite3
import glob
from dotfile import abs_path

filename = r'%APPDATA%\Mozilla\Firefox\Profiles\*default-release*/permissions.sqlite'
command = (
    'INSERT INTO moz_perms(origin, "type", permission, expireType, expireTime, modificationTime) '
    "SELECT :host, 'cookie', 1, 0, 0, 1636157572050 "
    'WHERE NOT EXISTS(SELECT 1 FROM moz_perms WHERE origin = :host);'
)


def sync_cookies(*args: str) -> None:
    conn = None
    try:
        db_path = glob.glob(abs_path(filename))[0]
        conn = sqlite3.connect(db_path)

        for origin in args:
            conn.cursor()\
                .execute(command, {'host': origin})

        conn.commit()
    finally:
        conn.close()
