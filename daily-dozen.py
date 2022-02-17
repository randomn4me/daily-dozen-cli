#!/usr/bin/python3

import argparse
import collections
import datetime
import json
import os

from tabulate import tabulate

storage = os.path.join(os.environ.get('HOME'), '.daily-dozen')

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


def read_user_input(text, max_num):
    user_input = input(f'{text} (max. {max_num}): ')
    try:
        user_num = int(user_input)
    except ValueError:
        if user_input == 'q':
            exit(0)
        print('Please insert a num or \'q\'')
        return read_user_input(text, max_num)
    return min(user_num, max_num)


def get_user_dozen():
    print('Let\'s read your dozen (quit with \'q\'):')
    dozen = collections.OrderedDict()

    for key in gregers_dozen.keys():
        dozen[key] = read_user_input(key, gregers_dozen[key])

    return dozen


def dozen_pretty_print(content_dict):
    print(tabulate(content_dict.items(), ['dozen', 'num'], tablefmt='psql'))


def write_file(user_dozen, path):
    with open(path, 'w') as f:
        f.write(json.dumps(user_dozen))


def read_file(path: str):
    with open(path, 'r') as f:
        return json.load(f)


def get_stored_files(num: int = 0):
    files = [f.name for f in os.scandir(storage) if os.path.isfile(f.path)]
    return sorted(files[-num:])


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

    print(f'+{(len(string) + 2) * "-"}+')


def details(date: str):
    date_file = os.path.join(storage, str(date))

    if os.path.isfile(date_file):
        content = read_file(date_file)
        print(f'Detailed dozen from {date}')
        dozen_pretty_print(content)
    else:
        print(f'No dozens logged for {date}')


def edit(num):
    date = today - datetime.timedelta(days=num)
    print(f'Editing dozen on {date}')
    edit_file = os.path.join(storage, str(date))

    if os.path.isfile(edit_file):
        content = read_file(edit_file)
        old_dozen = get_content_dozen(content)
        print(f'Your old dozen for {date}')
        dozen_pretty_print(old_dozen)

    user_dozen = get_user_dozen()
    dozen_pretty_print(user_dozen)
    write_file(user_dozen, edit_file)


def check_forgotten():
    day_delta = datetime.timedelta(days=1)

    files = get_stored_files()
    if not files:
        return
    date = datetime.date.fromisoformat(files[0])

    while date < today:
        if str(date) not in files:
            print(f'You forgot to log {date}')
        date += day_delta


def statistics(num=0):
    files = get_stored_files(num)

    stats = dict()
    for f in files:
        content = read_file(os.path.join(storage, f))
        dozen = get_content_dozen(content)
        stats[f] = sum([dozen[k] for k in dozen.keys() if k not in ['vitamine b12', 'vitamine d3']])

    return stats


def plot(stats_dict):
    for cur_value in range(sum(gregers_dozen.values()) - 2, 0, -1):
        print_dates = dict(stats_dict)
        for k, v in stats_dict.items():
            print_dates[k] = '#' if v >= cur_value else ' '

        print(f' {cur_value:2} | {"  ".join(print_dates.values())}')
        cur_value -= 1

    print(f'    +{"---" * len(print_dates)}-')
    print(f'date {" ".join([d[-2:] for d in stats_dict.keys()])}')


def graph(days):
    stats = statistics(days)
    plot(stats)
    exit(0)


def average(num=None):
    stats = statistics()

    averages = dict()
    cur_sum = 0
    for index, (date, sum_of_dozen) in enumerate(stats.items()):
        cur_sum += sum_of_dozen
        averages[date] = cur_sum / (index + 1)

    if num is not None:
        output = averages.items()[-num:]
    else:
        output = averages.items()

    print(tabulate(output, ['date', 'average'], tablefmt='psql'))
    exit(0)


def main():
    ap = argparse.ArgumentParser(
        description='Log your daily dozen of plant based essentials.',
        formatter_class=argparse.RawTextHelpFormatter)

    ap.add_argument('-l', '--last',
                    action='store_true', default=False,
                    help='Print last dozen')
    ap.add_argument('-e', '--edit', type=int, const=0, nargs='?',
                    help='Edit the n-th last entry (e.g. editing yesterday: -e 1) (defaults to 0)')
    ap.add_argument('-s', '--stats', type=int, const=7, nargs='?',
                    help='Show the sum of points for the last days (excluding b12, d3) (defaults to 7)')
    ap.add_argument('--details', type=str,
                    help='Print details of a certain date in iso format (e.g. 2018-07-20)')
    ap.add_argument('--graph', type=int, const=30, nargs='?',
                    help='Plotting statistic using upto the last n logs (defaults to 30).')
    ap.add_argument('--average', type=int, const=30, nargs='?',
                    help='Show the average for each day (defaults to 30).')

    args = ap.parse_args()

    if not os.path.isdir(storage):
        os.makedirs(storage)

    print(f'Welcome to daily dozen cli! Today is {today}')

    check_forgotten()

    if args.last:
        list_files()
    elif args.details is not None:
        try:
            if datetime.date.fromisoformat(args.details):
                details(args.details)
        except ValueError:
            usage(ap)
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
