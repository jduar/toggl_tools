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


def print_running():
    
    entry = toggl.running_entry()
    if entry == None:
        print("No Toggl entry is running.")
    else:
        description = running_description(entry)
        start_time, run_time = get_time(entry)

        print('>>> Running:      ' + description)
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
    entries = toggl.all_entries()
    entry_list = []
    
    for entry in entries:
        if is_entry_in_list(entry, entry_list) == False:
            entry_list.append(entry)

    print(">>> You can resume the following entries:")
    n = 1
    for entry in entry_list:
        print('> {} - {} [{}]'.format(str(n),
                                      entry['description'],
                                      ",".join([str(tag) for tag in entry['tags']])))
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
    

def main():
    
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--new', type=str,
                       help="Create a new Toggl entry.")
    group.add_argument('-s', '--stop', action='store_true',
                       help="Stop the running Toggl entry.")
    group.add_argument('--resume', action='store_true',
                       help="Resume a previous Toggl entry.")

    parser.add_argument('-t', '--tag', nargs='+',
                        help="Set tags for the new Toggl entry.")
    
    parser.add_argument('-r', '--running', default=False,
                        help="Check running Toggl entry.",
                        action='store_true')

    args = parser.parse_args()

    if args.running:
        print_running()

    if args.tag and args.new:
        start_toggl(str(args.new), args.tag)

    if args.resume:
        resume()
        
    '''
    if args.tag and not args.new:
        print("Incorrect usage.")
        exit()

    elif args.new:
        start_toggl(str(args.new))
    '''
    if args.stop:
        stop_toggl()

    
if __name__ == '__main__':
    main()
    read_api_key()
