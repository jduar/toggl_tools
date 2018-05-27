# toggl_tools

toggl_tools is a set of tools I'm writing to interact with the Toggl web app.

These should eventually include the following features:
* basic request handling and interaction with the Toggl API;
* a cli application to start, stop and check running entries from the terminal;
* a polybar plugin to keep track of running entries.

## config
To use these, you should place them somewhere and run them. A file named config should be placed on the same folder, containing only your Toggl API key.

toggl_cli.py depends on toggl_tools.py. They also require the following python modules:
* requests
* base64
* argparse