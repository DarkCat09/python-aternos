# Python Aternos API
An unofficial Aternos API written in Python.  
It uses requests, cloudscraper and lxml to parse data from [aternos.org](https://aternos.org/).

## Using
First you need to install the module:
```bash
pip install python-aternos
```

To use Aternos API in your Python script, import it and  
login with your username and password (or MD5 hash of password).  
> Note: Logging in with Google or Facebook account is not supported yet.

Then get the servers list using get_servers method.  
You can start/stop your Aternos server now, calling `start()` or `stop()`.

There is an example how to use the Aternos API:
```python
# Import
from python_aternos import Client

# Log in
#aternos = Client('USERNAME', password='PASSWORD')
aternos = Client('example', password='test123')
# ----OR----
#aternos = Client('USERNAME', md5='HASHED_PASSWORD')
aternos = Client('example', md5='cc03e747a6afbbcbf8be7668acfebee5')

# get_servers returns AternosServer list
atservers = aternos.servers

# If you have only one server, get it by 0 index
myserv = atservers[0]

# Start
myserv.start()
# Stop
myserv.stop()

# You can also find server by IP
testserv = None
for serv in atservers:
    if serv.address == 'test.aternos.org':
        testserv = serv
if testserv != None:
    # Prints a server softaware and its version
    # (for example, "Vanilla 1.12.2")
    print(testserv.software, testserv.version)
    # Starts server
    testserv.start()
```
You can find full documentation on the [Project Wiki](https://github.com/DarkCat09/python-aternos/wiki).

## License
[License Notice](NOTICE):
```
Copyright 2021 Chechkenev Andrey

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
You **don't** need to attribute me, if you are just using this module installed from PIP.
