# How-To 2: Controlling Minecraft server

In the previous part we logged into account and started a server.  
But python-aternos can do much more.

## Basic methods
```python
from python_aternos import Client

at = Client.from_credentials('username', 'password')
serv = at.list_servers()[0]

# Start
serv.start()

# Stop
serv.stop()

# Restart
serv.restart()

# Cancel starting
serv.cancel()

# Confirm starting
# at the end of a queue
serv.confirm()
```

## Starting
### Arguments
`start()` can be called with arguments:

 - headstart (bool): Start server in headstart mode
 which allows you to skip all queue.
 - accepteula (bool): Automatically accept Mojang EULA.

If you want to launch your server instantly, use this code:
```python
serv.start(headstart=True)
```

### Errors
`start()` raises `ServerStartError` if Aternos denies request.  
This object contains an error code, on which depends an error message.

 - EULA was not accepted (code: `eula`) -
 remove `accepteula=False` or run `serv.eula()` before startup.
 - Server is already running (code: `already`) -
 you don't need to start server, it is online.
 - Incorrect software version installed (code: `wrongversion`) -
 if you have *somehow* installed non-existent software version (e.g. `Vanilla 2.16.5`).
 - File server is unavailable (code: `file`) -
 problems in Aternos servers, view [https://status.aternos.gmbh](https://status.aternos.gmbh)
 - Available storage size limit has been reached (code: `size`) -
 files on your Minecraft server have reached 4GB limit
 (for exmaple, too much mods or loaded chunks).

Always wrap `start` into try-catch.
```python
from python_aternos import ServerStartError

...

try:
    serv.start()
except ServerStartError as err:
    print(err.code)     # already
    print(err.message)  # Server is already running
```

## Cancellation
Server launching can be cancelled only when you are waiting in a queue.  
After queue, when the server starts and writes something to the log,  
you can just `stop()` it, not `cancel()`.

## Server info
```python
>>> serv.address
'test.aternos.me:15172'

>>> serv.domain
'test.aternos.me'

>>> serv.subdomain
'test'

>>> serv.port
15172

>>> from python_aternos import Edition
>>> serv.edition
0
>>> serv.edition == Edition.java
True
>>> serv.edition == Edition.bedrock
False

>>> serv.software
'Forge'
>>> serv.version
'1.16.5 (36.2.34)'

>>> serv.players_list
['DarkCat09', 'jeb_']
>>> serv.players_count
2
>>> serv.slots
20

>>> print('Online:', serv.players_count, 'of', serv.slots)
Online: 2 of 20

>>> serv.motd
'§7Welcome to the §9Test Server§7!'

>>> from python_aternos import Status
>>> serv.css_class
'online'
>>> serv.status
'online'
>>> serv.status_num
1
>>> serv.status_num == Status.on
True
>>> serv.status_num == Status.off
False
>>> serv.status_num == Status.starting
False

>>> serv.restart()

# Title on web site: "Loading"
>>> serv.css_class
'loading'
>>> serv.status
'loading'
>>> serv.status_num
6
>>> serv.status_num == Status.loading
True
>>> serv.status_num == Status.preparing
False
>>> serv.status_num == Status.starting
False

# Title on web site: "Preparing"
>>> serv.css_class
'loading'
>>> serv.status
'preparing'
>>> serv.status_num
10
>>> serv.status_num == Status.preparing
True
>>> serv.status_num == Status.starting
False
>>> serv.status_num == Status.on
False

# Title on web site: "Starting"
>>> serv.css_class
'loading starting'
>>> serv.status
'starting'
>>> serv.status_num
2
>>> serv.status_num == Status.starting
True
>>> serv.status_num == Status.on
False

>>> serv.ram
2600
```

## Changing subdomain and MOTD
To change server subdomain or Message-of-the-Day,
just assign a new value to the corresponding fields:
```python
serv.subdomain = 'new-test-server123'
serv.motd = 'Welcome to the New Test Server!'
```

## Updating status
python-aternos don't refresh server information by default.  
This can be done with [WebSockets API](websocket) automatically
(but it will be explained later in the 6th part of how-to guide),  
or with `fetch()` method manually (much easier).

`fetch()` called also when an AternosServer object is created
to get info about the server:

 - full address,
 - MOTD,
 - software,
 - connected players,
 - status,
 - etc.

Use it if you want to see new data one time:
```python
import time
from python_aternos import Client

at = Client.from_credentials('username', 'password')
serv = at.list_servers()[0]

# Start
serv.start()
# Wait 10 sec
time.sleep(10)
# Check
serv.fetch()
print('Server is', serv.status)  # Server is online
```
But this method is **not** a good choice if you want to get real-time updates.  
Read [How-To 6: Real-time updates](websocket) about WebSockets API
and use it instead of refreshing data in a while-loop.

## Countdown
Aternos stops a server when there are no players connected.  
You can get remained time in seconds using `serv.countdown`.

For example:
```python
# Start
serv.start()

# Get the countdown value
print(serv.countdown, 'seconds')
# -1 seconds
# means "null" in countdown field

# Wait for start up
time.sleep(10)

# Refresh info
serv.fetch()
# Get countdown value
print(serv.countdown, 'seconds')
# 377 seconds

# Check if countdown changes
time.sleep(10)
serv.fetch()
print(serv.countdown, 'seconds')
# 367 seconds

# ---
# Convert to minutes and seconds
mins, secs = divmod(serv.countdown, 60)
print(f'{mins}:{secs:02}')  # 6:07
# OR
cd = serv.countdown
print(f'{cd // 60}:{cd % 60:02}')  # 6:07
```
