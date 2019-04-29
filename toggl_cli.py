#!/usr/bin/env python

import argparse
import time
import os
from toggl_tools import Toggl


toggl = Toggl()

### Timezone (??)
# UTC is 0
timezone = 1


def read_api_key():
    """Read the user's API key from the config file."""
    script_path = os.path.dirname(os.path.realpath(__file__))    
    config = open(script_path + '/config', 'r')
    api_key = config.readline().rstrip()
    config.close()
    return(api_key)


# Setting the API key. Need to reformat.
toggl.set_api_key(read_api_key())


def get_time(entry):
    """ Turns the date into a readable format."""
    entry_data = entry['data']
    time_str = entry_data['start']
    duration = entry_data['duration']
    
    # time_str example string:
    # 2018-05-25T18:21:13+00:00
    date = time_str[:10]
    
    # Adds the timezone to the given hour.
    start_hour = int(time_str[11:13]) + timezone
    start_time = str(start_hour) + time_str[13:19]

    # Calculates running duration.
    run_time = time.time() + duration
    hours = int(run_time // 3600)
    minutes = int((run_time // 60) - hours * 60)
    seconds = int(run_time % 60)
    
    run_time_str = ("%02d" % hours) + ':' + ("%02d" % minutes) + ':' + ("%02d" % seconds)
    
    return start_time, run_time_str


def running_description(entry):
    entry_data = entry['data']
    description = entry_data['description']
    return description


def running_tags(entry):
    entry_data = entry['data']
    tags = entry_data['tags']
    if tags == []:
        return None
    else:
        return tags


def print_running():
    entry = toggl.running_entry()
    if entry == None:
        print("No Toggl entry is running.")
    else:
        description = running_description(entry)
        tags = running_tags(entry)
        start_time, run_time = get_time(entry)
        print('>>> Running:      ' + description)
        if tags is not None:
            print('>>> Tags:         ' + ",".join(tags))
        print('>>> Start time:   ' + start_time)
        print('>>> Running for:  ' + run_time)
        
    # Decoding time.
    # Formatting everything.


def start_toggl(description, tags):   
    # Check if a task is running. If it is, print it.
    toggl.start_entry(description, tags=tags)
    print('>>> Starting:     ' + description)


def stop_toggl():
    entry = toggl.running_entry()
    if entry == None:
        print("No Toggl entry is running.")
    else:
        description = running_description(entry)
        start_time, run_time = get_time(entry)

        toggl.stop_entry()
        print('>>> Stopped       ' + description)
        print('>>> Start time:   ' + start_time)
        print('>>> Run time:     ' +     run_time)


def is_entry_in_list(entry, a_list):
    """Checks if an entry with the same description exists in given list."""
    for item in a_list:
        if entry['description'] == item['description']:
            return True
    return False


def resume():
    """Resumes a recent entry with all its properties."""
    # We now retrieve all entries in the previous month.
    # Getting the current date and the date from a month before.
    time_year = time.localtime()[0] 
    time_month = time.localtime()[1]
    time_day = time.localtime()[2]
    if time_month == 1:
        prev_time_month = 12
        prev_time_year = time_year - 1
    else:
        prev_time_month = time_month - 1
        prev_time_year = time_year

    cur_date = str(time_year) + '-' + ('%02d' % time_month) + '-' + ('%02d' % time_day)
    prev_date = str(prev_time_year) + '-' + ('%02d' % prev_time_month) + '-' + ('%02d' % time_day)

    entries = toggl.entries_between(prev_date, cur_date)
    entry_list = []
    
    for entry in entries:
        if is_entry_in_list(entry, entry_list) == False:
            entry_list.append(entry)

    print(">>> You can resume the following entries:")
    n = 1
    for entry in entry_list:
        tags = []
        if 'tags' in entry:
            [tags.append(i) for i in entry['tags']]
        print('> {} - {} [{}]'.format(str(n),
                                      entry['description'],
                                      ",".join(tags)))
        n += 1
    choice = int(input(">>> Type an entry number: "))

    if choice >= 1 and choice <= len(entry_list):
        res_entry = entry_list[choice-1]
        start_toggl(res_entry['description'], res_entry['tags'])
    else:
        print("You typed an unavailable number.")

    """
    >>> You can resume the following entries:
    > 1 - test [tag]
    > 2 - another [different_tag]
    >>> Type an entry number: 
    """


def add_entry(description, tags, duration):
    """Create a finished entry with a set duration."""
    time_year = time.localtime(time.time() - duration)[0] 
    time_month = time.localtime(time.time() - duration)[1]
    time_day = time.localtime(time.time() - duration)[2]
    time_hour = time.localtime(time.time() - duration)[3]
    time_min = time.localtime(time.time() - duration)[4]
    time_sec = time.localtime(time.time() - duration)[5]
        
    start_time = str(time_year) + '-' + ('%02d' % time_month) + '-' + ('%02d' % time_day + 'T' + str(time_hour) + ':' + str(time_min) + ':' + str(time_sec))

    print(start_time)
    #toggl.start_entry(description, start_time, duration, tags)
    
    print('>>> Created: ' + description)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--new', type=str,
                       help="Create a new Toggl entry.")
    group.add_argument('-s', '--stop', action='store_true',
                       help="Stop the running Toggl entry.")
    group.add_argument('-r', '--resume', action='store_true',
                       help="Resume a previous Toggl entry.")
    group.add_argument('-a', '--add', type=str,
                        help="Add a Toggl entry.")

    parser.add_argument('-d', '--duration',
                        help="Set duration for a done entry.")
    parser.add_argument('-t', '--tag', nargs='+',
                        help="Set tags for the new Toggl entry.")
    
    parser.add_argument('--running', default=False,
                        help="Check running Toggl entry.",
                        action='store_true')

    args = parser.parse_args()

    if args.running:
        print_running()

    elif args.tag and args.new:
        start_toggl(str(args.new), args.tag)

    elif args.tag and args.duration and args.add:
        add_entry(str(args.add), args.tag, int(args.duration))

    elif args.resume:
        resume()
        
    elif args.stop:
        stop_toggl()

    # Default behaviour is to show running entries.
    else:
        print_running()
    '''
    if args.tag and not args.new:
        print("Incorrect usage.")
        exit()

    elif args.new:
        start_toggl(str(args.new))
    '''

    read_api_key()