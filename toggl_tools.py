#!/usr/bin/env python

import requests
from base64 import b64encode


def check_internet():
    url = "https://www.toggl.com/"
    timeout = 25
    try:
        rq_test = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False


class Toggl():

    def __init__(self):
        # URLs
        self.url_current = 'https://www.toggl.com/api/v8/time_entries/current'
        self.url_start = 'https://www.toggl.com/api/v8/time_entries/start'
        self.url_entries = 'https://www.toggl.com/api/v8/time_entries'
        self.url_workspaces = 'https://www.toggl.com/api/v8/workspaces'

        self.headers = {
            'Authorization': '',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'User-Agent': 'python/requests'
        }

        self.user_agent = 'toggl_tools'

    
    # Setting the user's API key
    def set_api_key(self, api_key):
        """Obtaining and setting the api_key in the header."""
        auth_string = api_key + ':api_token'
        auth_string = "Basic " + b64encode(auth_string.encode()).decode('ascii').rstrip()

        self.headers['Authorization'] = auth_string


    def request(self, url):
        # Check for toggl.com availability
        if not check_internet():
            print("toggl.com unreachable")
            quit()
        """Making a get request."""
        r = requests.get(url, headers=self.headers)
        return r.json()
    #
    # --- 
    #
    def all_entries(self):
        """Returns all time entries."""
        entries = self.request(self.url_entries)
        return entries


    def entries_between(self, start_date, end_date, start_time='00:00:00', end_time='23:59:59', timezone='00:00'):
        """Returns all entries between two dates."""
        start_time_str = 'T{}%3A{}%3A{}'.format(start_time[0:2],
                                               start_time[3:5],
                                               start_time[6:])
        end_time_str = 'T{}%3A{}%3A{}'.format(end_time[0:2],
                                             end_time[3:5],
                                             end_time[6:])
        timezone_str = '%2B{}%3A{}'.format(timezone[0:2], timezone[3:])
        
        url = self.url_entries + '?start_date={}{}{}&end_date={}{}{}'.format(start_date, start_time_str, timezone_str, end_date, end_time_str, timezone_str)
        
        entries = self.request(url)
        return entries
        
        """
        2013-03-10, 2013-03-12, 15:42:46, 15:42:46, 02:00
        
        https://www.toggl.com/api/v8/time_entries?start_date=2013-03-10T15%3A42%3A46%2B02%3A00&end_date=2013-03-12T15%3A42%3A46%2B02%3A00
        """
    
    
    def workspaces(self):
        """Returns a list with the ids of one or more workspaces."""
        workspaces = self.request(self.url_workspaces)
        array = []
        for workspace in workspaces:
            array.append(workspace['id'])
        return array
        
    
    #
    # --- Handling running entries. ---
    #
    
    def running_entry(self):
        """Returns the running Toggl entry or None if none exists."""
        run_entry = self.request(self.url_current)
        if run_entry['data'] == None:
            return None
        else:
            return run_entry
        
    
    def start_entry(self, description, start_time=None, duration=None, tags=None, wid=None):
        """Starts a new entry."""

        """
        I need to either include a pid, wid, or detect the wid if none
        is present.
        
        """
        
        data = {
            'time_entry': {
            'description': description,
            'created_with': self.user_agent
            }
        }

        if start_time != None:
            data['time_entry']['start'] = start_time

        if duration != None:
            data['time_entry']['duration'] = duration

        if tags != None and type(tags) is list:
            data['time_entry']['tags'] = tags

        # If no wid is given, a default workspace is used.
        if wid == None:
            data['time_entry']['wid'] = self.workspaces()[0]

        response = requests.post(self.url_start, json=data, headers=self.headers)
        

    def stop_entry(self):
        """ Stops running entry."""
        
        entry = self.running_entry()
        if entry == None:
            return None
        else:
            entry_id = entry['data']['id']
            put_url = self.url_entries + '/' + str(entry_id) + '/stop'
            requests.put(put_url, headers=self.headers)
