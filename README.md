# Python Aternos API
An unofficial Aternos API written in Python.  
It uses [aternos](https://aternos.org/)' private API and html parsing.

## Installing
```bash
pip install python-aternos
```
> Note for Windows users:  
Install `lxml` package from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml) if you have a problem with it,  
and then execute `pip install --no-deps python-aternos`

## Usage
To use Aternos API in your Python script, import it
and login with your username and password/MD5.

Then request the servers list using `list_servers()`.  
You can start/stop your Aternos server now, calling `start()` or `stop()`.

Here is an example how to use the API:
```python
# Import
from python_aternos import Client

# Log in
aternos = Client.from_credentials('example', 'test123')
# ----OR----
aternos = Client.from_hashed('example', 'cc03e747a6afbbcbf8be7668acfebee5')

# Returns AternosServer list
servs = aternos.list_servers()

# Get the first server by the 0 index
myserv = servs[0]

# Start
myserv.start()
# Stop
myserv.stop()

# You can also find server by IP
testserv = None
for serv in servs:
    if serv.address == 'test.aternos.org':
        testserv = serv
if testserv != None:
    # Prints a server softaware and its version
    # (for example, "Vanilla 1.12.2")
    print(testserv.software, testserv.version)
    # Starts server
    testserv.start()
```
~~You can find full documentation on the [Project Wiki](https://github.com/DarkCat09/python-aternos/wiki).~~

## [More examples](/examples)

## Changelog
|Version|Description|
|:-----:|:-----------|
|v0.1|The first release.|
|v0.2|Fixed import problem.|
|v0.3|Implemented files API, added typization.|
|v0.4|Implemented configuration API, some bugfixes.|
|v0.5|The API was updated corresponding to new Aternos security methods. Huge thanks to [lusm554](https://github.com/lusm554).|
|v0.6/v1.0.0|Code refactoring, websockets API and session saving to prevent detecting automation access.|
|v1.0.1|Cloudflare bypassing fix, changed versioning (follows SemVer).|
|v1.1.x|Full implementation of config and software API, unit tests and documentation is planned.|
|v1.2.x|Shared access API and Google Drive backups is planned.|

## License
[License Notice](NOTICE):
```
Copyright 2021 Chechkenev Andrey, lusm554

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
You **don't** need to attribute me, if you are just using this module installed from PIP or wheel.
