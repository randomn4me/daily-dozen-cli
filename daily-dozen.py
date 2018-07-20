#!/usr/bin/python3

import argparse
import datetime
import os
import json
import sys

from collections import OrderedDict
from tabulate import tabulate

storage = os.path.join(
        os.environ.get('HOME', os.path.expanduser('~')), '.daily-dozen')

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


def usage(ap):
    ap.print_help()
    exit(1)

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

def dozen_pretty_print(content_dict):
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

def get_stored_files(num=None):
    files = sorted([f for f in os.listdir(storage) if
        os.path.isfile(os.path.join(storage, f))])
    if num is not None and num > 0:
        return files[-num:]
    return files


def list_files():
    last_files = get_stored_files()

    string = 'Your last dozen'
    print(f'+{(len(string)+2) * "-"}+')
    print(f'| {string} |')
    print(f'+{(len(string)+2) * "-"}+')

    for f in last_files:
        print(f'| {f:{len(string)}} |')

    print(f'+{(len(string)+2) * "-"}+')

    exit(0)

def details(date):
    date_file = os.path.join(storage, str(date))

    if os.path.isfile(date_file):
        content = read_file(date_file)
        print('detailed dozen')
        dozen_pretty_print(content)
    else:
        print(f'No stored dozens for {date}')

    exit(0)

def edit(date):
    edit_file = os.path.join(storage, str(date))

    if os.path.isfile(edit_file):
        old_dozen = read_file(edit_file)
        print('Your old dozen you want to edit')
        dozen_pretty_print(old_dozen)

    user_dozen = get_dozen()
    dozen_pretty_print(user_dozen)
    write_file(user_dozen, edit_file)

    exit(0)

def statistics(num):
    files = get_stored_files(num)
    gregers_without = [k for k in gregers_dozen.keys() if k not in ['vitamine b12', 'vitamine d3']]

    stats = dict()
    for f in files:
        dozen = read_file(os.path.join(storage, f))
        stats[f] = sum(list(dozen.values()))

    print(tabulate(stats.items(), ['date', 'sum'], tablefmt='psql'))
    exit(0)

def main():
    ap = argparse.ArgumentParser(
            description='Store your daily dozen of plant based essentials.',
            formatter_class=argparse.RawTextHelpFormatter)

    ap.add_argument('-l', '--last',
            action='store_true', default=False,
            help='Print last dozen')
    ap.add_argument('-d', '--details', type=str,
            help='Print details of a certain date in iso format (e.g. 2018-07-20)')
    ap.add_argument('-e', '--edit', type=int, const=0, nargs='?',
            help='Edit the n-th last entry [defaults to 0] (e.g. editing yesterday: -e 1)')
    ap.add_argument('-s', '--stats', type=int, const=7, nargs='?',
            help='Show the sum of points for the last days (excluding b12, d3) [defaults to 7]')

    args = ap.parse_args()

    if not os.path.isdir(storage):
        os.makedirs(storage)

    print(f'Welcome to daily dozen cli! Today is {today}')

    if args.last:
        list_files()
    elif args.details is not None:
        try:
            year, month, day = map(int, args.details.split('-'))
            date = datetime.date(year, month, day)
        except ValueError:
            usage(ap)
        details(date)
    elif args.edit is not None:
        if args.edit < 0:
            usage(ap)
        edit(today - datetime.timedelta(days=args.edit))
    elif args.stats is not None:
        statistics(args.stats)
    else:
        today_file = os.path.join(storage, str(today))

        if os.path.isfile(today_file):
            content = read_file(today_file)
            print('todays dozen')
            dozen_pretty_print(content)
            exit(0)

        user_dozen = get_dozen()
        dozen_pretty_print(user_dozen)
        write_file(user_dozen, today_file)


if __name__ == '__main__':
    main()
