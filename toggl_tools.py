#!/usr/bin/env python

import requests
from base64 import b64encode


class Toggl():

    def __init__(self):
        # URLs
        self.url_current = 'https://www.toggl.com/api/v8/time_entries/current'
        self.url_start = 'https://www.toggl.com/api/v8/time_entries/start'
        self.url_entries = 'https://www.toggl.com/api/v8/time_entries/'

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
        """Making a get request."""
        r = requests.get(url, headers=self.headers)
        return r.json()
    #
    # --- Entry details.
    #

    def entry_details(self, entry_id):

        get_url = self.url_entries + str(entry_id)
        entry = self.request(get_url)
        return entry
    
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
        
    
    def start_entry(self, description, tags=[]):
        """Starts a new entry."""

        """
        I need to either include a pid, wid, or detect the wid if none
        is present.
        
        """
        
        wid = 2748043
        
        data = {
            'time_entry': {
            'description': description,
            'tag': tags,
            'wid': wid,
            'created_with': self.user_agent
            }
        }
        response = requests.post(self.url_start, json=data, headers=self.headers)
        #print(response.text)


    def stop_entry(self):
        """ Stops running entry."""
        
        entry = self.running_entry()
        if entry == None:
            return None
        else:
            entry_id = entry['data']['id']
            put_url = self.url_entries + str(entry_id) + '/stop'
            requests.put(put_url, headers=self.headers)
