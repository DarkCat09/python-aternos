# How-To 1: Logging in

## Intro
Firstly, let's install the library using the command from ["Common install" section](../../#common).
```bash
pip install python-aternos
```

Also, [register](https://aternos.org/go/) an Aternos account if you haven't one.  
Now you are ready.

## Authorization with password
Import python-aternos module:
```python
from python_aternos import Client
```

Then, you can log in to your account using from_credentials method
specifying your username and password.
```python
at = Client.from_credentials('username', 'password')
```
This line will create Client object and save it to `at` variable.

Okay, we are logged in. What's next?

## Servers list
Request the list of your servers:
```python
servers = at.list_servers()
```

This variable must contain something like:
```python
[<python_aternos.atserver.AternosServer object at 0x7f97bd8b5690>]
```

If you have only one server in your account,
get it by the zero index:
```python
serv = servers[0]
```

Otherwise, iterate over the list to find it by IP or subdomain:

```python
# 1st way: For-loop
# Our server: test.aternos.me

# Find by IP (domain)
serv = None
for s in servers:
    if s.domain == 'test.aternos.me':
        serv = s

# Or find by subdomain
# (part before .aternos.me)
serv = None
for s in servers:
    if s.subdomain == 'test':
        serv = s

# Important check
if serv is None:
    print('Not found!')
    exit()
```

```python
# 2nd way: Dict comprehension

serv = {
    'serv': s
    for s in servers
    if s.subdomain == 'test'
}.get('serv', None)

if serv is None:
    print('Not found!')
    exit()
```

`serv` is an AternosServer object. I'll explain it more detailed in the next part.  
Now, let's just try to start and stop server:
```python
# Start
serv.start()

# Stop
serv.stop()
```

## Saving session
In the version `v2.0.1` and above,
python-aternos automatically saves and restores session cookie,
so you don't need to do it by yourself now.

Before, you should save session manually:
```python
# This code is useless in new versions,
# because they do it automatically.

from python_aternos import Client

at = Client.from_credentails('username', 'password')
myserv = at.list_servers()[0]

...

at.save_session()

# Closing python interpreter
# and opening it again

from python_aternos import Client

at = Client.restore_session()
myserv = at.list_servers()[0]

...
```
Function `save_session()` writes session cookie and cached servers list to `.aternos` file in your home directory.  
`restore_session()` creates Client object from session cookie and restores servers list.  
This feature reduces the count of network requests and allows you to log in and request servers much faster.

If you created a new server, but it doesn't appear in `list_servers` result, call it with `cache=False` argument.
```python
# Refreshing list
servers = at.list_servers(cache=False)
```

## Username, email, password
Change them using the corresponding methods:
```python
at.change_username('new1cool2username3')
at.change_password('old_password', 'new_password')
at.change_email('new@email.com')
```

## Hashing passwords
For security reasons, Aternos API takes MD5 hashed passwords, not plain.

`from_credentials` hashes your credentials and passes to `from_hashed` classmethod.  
`change_password` also hashes passwords and calls `change_password_hashed`.  
And you can use these methods too.  
Python-Aternos contains a handy function `Client.md5encode` that can help you with it.

```python
>>> from python_aternos import Client
>>> Client.md5encode('old_password')
'0512f08120c4fef707bd5e2259c537d0'
>>> Client.md5encode('new_password')
'88162595c58939c4ae0b35f39892e6e7'
```

```python
from python_aternos import Client

my_passwd = '0512f08120c4fef707bd5e2259c537d0'
new_passwd = '88162595c58939c4ae0b35f39892e6e7'

at = Client.from_hashed('username', my_passwd)

at.change_password_hashed(my_passwd, new_passwd)
```

## Two-Factor Authentication
...
