#!/usr/bin/python3

import argparse
import datetime
import os
import json

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
    'spices': 1,
    'grains': 3,
    'beverages': 5,
    'exercise': 1,
    'vitamine b12': 1,
    'vitamine d3': 1
}


def usage(ap):
    ap.print_help()
    exit(1)

def quitting():
    print('Quitting daily dozen. Aborting action.')
    exit(0)

def iso_to_date(isoformat_string):
    try:
        year, month, day = map(int, isoformat_string.split('-'))
        date = datetime.date(year, month, day)
        return date
    except:
        print('error reading date')
        quitting()

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

def get_user_dozen():
    print('Let\'s read your dozen (quit with \'q\'):')
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
        print(f'Writing to file {file_name} failed. Abort.')
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

def get_content_dozen(content_dict):
    copy = dict(content_dict)
    for key in copy.keys():
        if key not in gregers_dozen.keys():
            del copy[key]
    return copy

def list_files():
    last_files = get_stored_files()

    string = 'Your last dozen'
    print(f'+{(len(string) + 2) * "-"}+')
    print(f'| {string} |')
    print(f'+{(len(string) + 2) * "-"}+')

    for f in last_files:
        print(f'| {f:{len(string)}} |')

    print(f'+{(len(string)+2) * "-"}+')

    exit(0)

def details(date):
    date_file = os.path.join(storage, str(date))

    if os.path.isfile(date_file):
        content = read_file(date_file)
        print(f'detailed dozen from {date}')
        dozen_pretty_print(content)
    else:
        print(f'No dozens logged for {date}')

    exit(0)

def edit(num):
    date = today - datetime.timedelta(days=num)
    print(f'editing dozen for date {date}')
    edit_file = os.path.join(storage, str(date))

    if os.path.isfile(edit_file):
        content = read_file(edit_file)
        old_dozen = get_content_dozen(content)
        print(f'Your old dozen for {date}')
        dozen_pretty_print(old_dozen)

    user_dozen = get_user_dozen()
    dozen_pretty_print(user_dozen)
    write_file(user_dozen, edit_file)

    exit(0)

def check_forgotten():
    day_delta = datetime.timedelta(days=1)

    files = get_stored_files()
    date = iso_to_date(files[0])

    while date < today:
        if str(date) not in files:
            print(f'You forgot to log {date}')
        date += day_delta

def statistics(num=None):
    files = get_stored_files(num)

    stats = dict()
    for f in files:
        content = read_file(os.path.join(storage, f))
        dozen = get_content_dozen(content)
        stats[f] = sum([dozen[k] for k in dozen.keys() if k not in ['vitamine b12', 'vitamine d3']])

    return stats

def plot(stats_dict):
    values = stats_dict.values()
    cur_value = 24

    print()
    while cur_value > 0:
        print_dates = dict(stats_dict)
        for k, v in stats_dict.items():
            print_dates[k] = '^' if v >= cur_value else ' '

        print(f'{cur_value:2} | {"  ".join(print_dates.values())}')
        cur_value -= 1

    print(f'   +{"---" * len(print_dates)}-')

    print(f'    {" ".join([d[-2:] for d in stats_dict.keys()])}')

def graph(days):
    stats = statistics(days)
    plot(stats)
    exit(0)

def average():
    stats = statistics()

    averages = dict()
    cur_sum = 0
    for index, (date, sum_of_dozen) in enumerate(stats.items()):
        cur_sum += sum_of_dozen
        averages[date] = cur_sum / (index + 1)

    print(tabulate(averages.items(), ['date', 'average'], tablefmt='psql'))
    exit(0)

def main():
    ap = argparse.ArgumentParser(
            description='Log your daily dozen of plant based essentials.',
            formatter_class=argparse.RawTextHelpFormatter)

    ap.add_argument('-l', '--last',
            action='store_true', default=False,
            help='Print last dozen')
    ap.add_argument('-e', '--edit', type=int, const=0, nargs='?',
            help='Edit the n-th last entry (e.g. editing yesterday: -e 1) [defaults to 0]')
    ap.add_argument('-s', '--stats', type=int, const=7, nargs='?',
            help='Show the sum of points for the last days (excluding b12, d3) [defaults to 7]')
    ap.add_argument('--details', type=str,
            help='Print details of a certain date in iso format (e.g. 2018-07-20)')
    ap.add_argument('--graph', type=int, const=30, nargs='?',
            help='Plotting statistic using upto the last n logs [defaults to 30].')
    ap.add_argument('--average', action='store_true', default=False,
            help='Show the average for each day.')

    args = ap.parse_args()

    if not os.path.isdir(storage):
        os.makedirs(storage)

    print(f'Welcome to daily dozen cli! Today is {today}')

    check_forgotten()

    if args.last:
        list_files()
    elif args.details is not None:
        try:
            date = iso_to_date(args.details)
        except ValueError:
            usage(ap)
        details(date)
    elif args.edit is not None:
        if args.edit < 0:
            usage(ap)
        edit(args.edit)
    elif args.stats is not None:
        stats = statistics(args.stats)
        print(tabulate(stats.items(), ['date', 'sum'], tablefmt='psql'))
        exit(0)
    elif args.graph is not None:
        graph(args.graph)
    elif args.average:
        average()
    else:
        today_file = os.path.join(storage, str(today))

        if os.path.isfile(today_file):
            content = read_file(today_file)
            print('todays dozen')
            dozen_pretty_print(content)
            exit(0)

        user_dozen = get_user_dozen()
        dozen_pretty_print(user_dozen)
        write_file(user_dozen, today_file)


if __name__ == '__main__':
    main()
