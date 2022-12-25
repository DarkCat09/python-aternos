# How-To 3: Players lists
You can add a player to operators,
include into the whitelist or ban him
using this feature.

## Common usage
It's pretty easy:
```python
from python_aternos import Client, Lists

...

whitelist = serv.players(Lists.whl)

whitelist.add('jeb_')
whitelist.remove('Notch')

whitelist.list_players()
# ['DarkCat09', 'jeb_']
```

## List types

|    Name    |  Enum key |
|:----------:|:---------:|
|  Whitelist |`Lists.whl`|
|  Operators |`Lists.ops`|
|   Banned   |`Lists.ban`|
|Banned by IP|`Lists.ips`|

For example, I want to ban someone:
```python
serv.players(Lists.ban).add('someone')
```

And give myself the operator rights:
```python
serv.players(Lists.ops).add('DarkCat09')
```

Unban someone:
```python
serv.players(Lists.ban).remove('someone')
```

Unban someone who I banned by IP:
```python
serv.players(Lists.ips).remove('anyone')
```

## Caching
If `list_players` doesn't show added players, call it with `cache=False` argument, like list_servers.
```python
lst = serv.players(Lists.ops)
lst.list_players(cache=False)
# ['DarkCat09', 'jeb_']
```
