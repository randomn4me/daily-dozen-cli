import os
import json
from collections import OrderedDict
from datetime import date

cache_dir = os.path.join(
        os.environ.get('XDG_CACHE_HOME', os.path.expanduser(os.path.join('~', '.cache'))), 
        'daily-dozen-cli')

today = date.today()

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
    'beverages': 5
}


def read_user_input(text, max_num):
    user_input = input(f'{text}: ')
    try:
        user_num = int(user_input)
    except ValueError:
        print("Please insert a num")
        return read_user_input(text, max_num)
    return min(user_num, max_num)


def get_dozen():
    print('Let\'s read your dozen\n')
    dozen = OrderedDict()

    for key in gregers_dozen.keys():
        dozen[key] = read_user_input(key, gregers_dozen[key])

    return dozen


def pretty_print(content):
    print(content)


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


def main():
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)

    print(f"Welcome to daily dozen cli\nToday is {today}")

    today_file = os.path.join(cache_dir, str(today))

    if os.path.isfile(today_file):
        content = read_file(today_file)
        print('Todays dozen:')
        pretty_print(content)
        return

    user_dozen = get_dozen()

    print(f'Storing {user_dozen} to {today_file}')
    write_file(user_dozen, today_file)



if __name__ == '__main__':
    main()
