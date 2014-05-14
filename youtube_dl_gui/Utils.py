#! /usr/bin/env python

import os
import sys
import locale
import subprocess

from os import (
    remove as remove_file,
    makedirs as makedir,
    name as os_type,
)

from os.path import (
    getsize as get_filesize,
    exists as file_exist
)

from .data import __appname__


def get_encoding():
    if sys.version_info >= (3, 0):
        return None

    if sys.platform == 'win32':
        try:
            enc = locale.getpreferredencoding()
            u'TEST'.encode(enc)
        except:
            enc = 'UTF-8'
        return enc
    return None


def encode_list(lst, encoding):
    return [item.encode(encoding, 'ignore') for item in lst]


def video_is_dash(video):
    return "DASH" in video


def audio_is_dash(audio):
    return audio != "none"


def path_seperator():
    ''' Return path seperator for current OS '''
    return '\\' if os_type == 'nt' else '/'


def fix_path(path):
    ''' Add path seperator at the end of the path
    if not exist and replace ~ with user $HOME '''
    if path == '':
        return path

    if path[-1:] != path_seperator():
        path += path_seperator()

    path_list = path.split(path_seperator())
    for index, item in enumerate(path_list):
        if item == '~':
            path_list[index] = get_home()

    path = path_seperator().join(path_list)
    return path


def get_home():
    return os.path.expanduser("~")


def abs_path(filename):
    path = os.path.realpath(os.path.abspath(filename))
    path = path.split(path_seperator())
    path.pop()
    return path_seperator().join(path)


def get_filename(path):
    return path.split(path_seperator())[-1]


def open_dir(path):
    if os_type == 'nt':
        os.startfile(path)
    else:
        subprocess.call(('xdg-open', path))


def check_path(path):
    if not file_exist(path):
        makedir(path)


def get_youtubedl_filename():
    youtubedl_fl = 'youtube-dl'
    if os_type == 'nt':
        youtubedl_fl += '.exe'
    return youtubedl_fl


def get_user_config_path():
    if os_type == 'nt':
        path = os.getenv('APPDATA')
    else:
        path = fix_path(get_home()) + '.config'
    return path


def shutdown_sys(password=''):
    if os_type == 'nt':
        subprocess.call(['shutdown', '/s', '/t', '1'])
    else:
        if password == '':
            subprocess.call(['/sbin/shutdown', '-h', 'now'])
        else:
            p = subprocess.Popen(
                ['sudo', '-S', '/sbin/shutdown', '-h', 'now'],
                stdin=subprocess.PIPE
            )
            p.communicate(password + '\n')


def get_time(seconds):
    ''' Return day, hours, minutes, seconds from given seconds'''
    dtime = {'seconds': 0, 'minutes': 0, 'hours': 0, 'days': 0}

    if seconds < 60:
        dtime['seconds'] = seconds
    elif seconds < 3600:
        dtime['minutes'] = seconds / 60
        dtime['seconds'] = seconds % 60
    elif seconds < 86400:
        dtime['hours'] = seconds / 3600
        dtime['minutes'] = seconds % 3600 / 60
        dtime['seconds'] = seconds % 3600 % 60
    else:
        dtime['days'] = seconds / 86400
        dtime['hours'] = seconds % 86400 / 3600
        dtime['minutes'] = seconds % 86400 % 3600 / 60
        dtime['seconds'] = seconds % 86400 % 3600 % 60

    return dtime


def get_icon_path():
    ''' Return icon path else return None. Search package_path/icons, settings_path/icons
    $HOME/.icons, $XDG_DATA_DIRS/icons, /usr/share/pixmaps in that order'''
    SIZES = ('256x256', '128x128', '64x64', '32x32', '16x16')
    ICON_NAME = 'youtube-dl-gui_'
    ICON_EXTENSION = '.png'

    ICONS_LIST = [ICON_NAME + s + ICON_EXTENSION for s in SIZES]

    # Package path backwards 2 times
    # e.g. /home/user/test/t1/t2
    # /home/user/test/t1/t2/icons
    # /home/user/test/t1/icons
    path = abs_path(__file__)
    for i in range(2):
        temp_path = fix_path(path) + 'icons'

        for icon in ICONS_LIST:
            p = fix_path(temp_path) + icon

            if file_exist(p):
                return p

        path = path.split(path_seperator())
        path.pop()
        path = path_seperator().join(path)

    # Settings path icons/
    path = fix_path(get_user_config_path()) + __appname__.lower()
    path = fix_path(path) + 'icons'
    for icon in ICONS_LIST:
        temp_path = fix_path(path) + icon
        
        if file_exist(temp_path):
            return temp_path

    # $HOME/.icons 
    path = fix_path(get_home()) + '.icons'

    for icon in ICONS_LIST:
        temp_path = fix_path(path) + icon

        if file_exist(temp_path):
            return temp_path

    # $XDG_DATA_DIRS/icons
    path = os.getenv('XDG_DATA_DIRS')
    for temp_path in path.split(':'):
        temp_path = fix_path(temp_path) + 'icons'
        temp_path = fix_path(temp_path) + 'hicolor'

        for size in SIZES:
            p = fix_path(temp_path) + size
            p = fix_path(p) + 'apps'
            p = fix_path(p) + ICON_NAME + size + ICON_EXTENSION

            if file_exist(p):
                return p

    # /usr/share/pixmaps
    path = '/usr/share/pixmaps/'
    for icon in ICONS_LIST:
        temp_path = path + icon

        if file_exist(temp_path):
            return temp_path

    return None
