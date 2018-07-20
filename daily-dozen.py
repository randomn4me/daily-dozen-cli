#!/usr/bin/python3

import argparse
import datetime
import os
import json
import sys

from collections import OrderedDict
from tabulate import tabulate

cache_dir = os.path.join(
        os.environ.get('XDG_CACHE_HOME', os.path.expanduser(os.path.join('~', '.cache'))), 
        'daily-dozen-cli')

today = datetime.date.today()

gregers_dozen = {
    'beans': 3,
    'berries': 1,
    'fruits': 3,
    'cruciferous': 1,
    'greens': 2,
    'vegetables': 2,
    'flaxseed': 1,
    'nuts': 1,
    'grains': 3,
    'spices': 1,
    'exercise': 1,
    'beverages': 5,
    'vitamine b12': 1,
    'vitamine d3': 1
}

string_size = max([len(s) for s in gregers_dozen.keys()])


def quitting():
    exit(0)

def read_user_input(text, max_num):
    user_input = input(f'{text} (max. {max_num}): ')
    try:
        user_num = int(user_input)
    except ValueError:
        if user_input is 'q':
            quitting()
        print("Please insert a num or 'q'")
        return read_user_input(text, max_num)
    return min(user_num, max_num)

def get_dozen():
    print('Let\'s read your dozen:')
    dozen = OrderedDict()

    for key in gregers_dozen.keys():
        dozen[key] = read_user_input(key, gregers_dozen[key])

    return dozen

def pretty_print(content_dict):
    print(tabulate(content_dict.items(), ['dozen', 'num'], tablefmt='psql'))

def write_file(user_dozen, file_name):
    try:
        with open(file_name, 'w') as f:
            f.write(json.dumps(user_dozen))
    except:
        print(f'Writing to file {file_name} failed.\nReverting operation')
        if os.path.isfile(file_name):
            os.remove(file_name)
        exit(1)

def read_file(file_name):
    try:
        with open(file_name, 'r') as f:
            content = f.read()
            return json.loads(content)
    except:
        print(f'Reading file {file_name} failed.')
        exit(1)

def list_files(details):
    last_files = sorted([f for f in os.listdir(cache_dir) if
            os.path.isfile(os.path.join(cache_dir, f))])
    if details:
        for f in last_files:
            print(f'Dozen of {f}')
            path = os.path.join(cache_dir, f)
            old_dozen = read_file(path)
            pretty_print(old_dozen)
    else:
        string = 'Your last dozen'
        print(f'+{(len(string)+2) * "-"}+')
        print(f'| {string} |')
        print(f'+{(len(string)+2) * "-"}+')
        for f in last_files:
            print(f'| {f:{len(string)}} |')

        print(f'+{(len(string)+2) * "-"}+')
    exit(0)

def edit(date):
    edit_file = os.path.join(cache_dir, str(date))

    if os.path.isfile(edit_file):
        old_dozen = read_file(edit_file)
        print('Your old dozen you want to edit')
        pretty_print(old_dozen)

    user_dozen = get_dozen()
    pretty_print(user_dozen)
    write_file(user_dozen, edit_file)

    exit(0)

def main():
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)

    ap = argparse.ArgumentParser(
            description='Store your daily dozen of plant based essentials.',
            formatter_class=argparse.RawTextHelpFormatter)

    ap.add_argument('-l', '--last',
            action='store_true', default=False,
            help='Print last dozen')
    ap.add_argument('-d', '--details',
            action='store_true', default=False,
            help='Print details (assumes --last)')
    ap.add_argument('-e', '--edit', type=int,
            help='Edit the n-th last entry (e.g. editing today: -e 0)')

    args = ap.parse_args()

    print(f'Welcome to daily dozen cli! Today is {today}')

    if args.last:
        list_files(args.details)
    elif args.edit is not None:
        if args.edit < 0:
            ap.print_help()
            exit(1)

        edit(today - datetime.timedelta(days=args.edit))

    today_file = os.path.join(cache_dir, str(today))

    if os.path.isfile(today_file):
        content = read_file(today_file)
        print('todays dozen')
        pretty_print(content)
        exit(0)

    user_dozen = get_dozen()
    pretty_print(user_dozen)
    write_file(user_dozen, today_file)


if __name__ == '__main__':
    main()
