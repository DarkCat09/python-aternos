# How-To 4: Files

## Intro
In python-aternos, all files on your Minecraft server
are represented as atfile.AternosFile objects.

They can be accessed through atfm.FileManager instance,
let's assign it to `fm` variable:
```python
>>> fm = serv.files()
```

## List directory contents
```python
>>> root = fm.list_dir('/')
[<python_aternos.atfile.AternosFile object at 0x7f1b0...>, ...]
```

## Get file by its path
```python
>>> myfile = fm.get_file('/server.properties')
<python_aternos.atfile.AternosFile object at 0x7f1b0...>
```

## File info
AternosFile object can point to
both a file and a directory
and contain almost the same properties and methods.
(So it's more correct to call it "Object in the server's filesystem",
but I chose an easier name for the class.)

 - `path` - Full path to the file **including leading** slash and **without trailing** slash.
 - `name` - Filename with extension **without leading** slash.
 - `dirname` - Full path to the directory which contains the file **without trailing** slash.
 - `is_file` and `is_dir` - File type in boolean.
 - `ftype` - File type in `FileType` enum value:
     - `FileType.file`
     - `FileType.dir` and `FileType.directory`
 - `size` - File size in bytes, float.  
 `0.0` for directories and
 `-1.0` when an error occurs.
 - `deleteable`, `downloadable` and `editable` are explained in the next section.

### File
```python
>>> f = root[5]

>>> f.path
'/server.properties'
>>> f.name
'server.properties'
>>> f.dirname
''

>>> f.is_file
False
>>> f.is_dir
True

>>> from python_aternos import FileType
>>> f.ftype == FileType.file
True
>>> f.ftype == FileType.directory
False

>>> f.size
1240.0

>>> f.deleteable
False
>>> f.downloadable
False
>>> f.editable
False
```

### Directory
```python
>>> f = root[2]

>>> f.path
'/config'
>>> f.name
'config'
>>> f.dirname
''

>>> f.is_file
False
>>> f.is_dir
True

>>> from python_aternos import FileType
>>> f.ftype == FileType.file
False
>>> f.ftype == FileType.directory
True
>>> f.ftype == FileType.dir
True

>>> f.size
0.0

>>> f.deleteable
False
>>> f.downloadable
True
>>> f.editable
False
```

## Methods

 - `get_text` returns the file content from the Aternos editor page
 (opens when you click on the file on web site).
 - `set_text` is the same as "Save" button in the Aternos editor.
 - `get_content` requests file downloading and
 returns file content in `bytes` (not `str`).  
 If it is a directory, Aternos returns its content in a ZIP file.
 - `set_content` like `set_text`, but takes `bytes` as an argument.
 - `delete` removes file.
 - `create` creates a new file inside this one  
 (if it's a directory, otherwise throws RuntimeWarning).

### Deletion and downloading rejection
In [Aternos Files tab](https://aternos.org/files),
some files can be removed with a red button, some of them is protected.  
You can check if the file is deleteable this way:
```python
>>> f.deleteable
False
```
`delete()` method will warn you if it's undeleteable,
and then you'll probably get `FileError`
because of Aternos deletion denial.

The same thing with `downloadable`.
```python
>>> f.downloadable
True
```
`get_content()` will warn you if it's undownloadable. 
And then you'll get `FileError`.

And `editable` means that you can click on the file
in Aternos "Files" tab to open editor.
`get_text()` will warn about editing denial.

### Creating files
Calling `create` method only available for directories
(check it via `f.is_dir`).  
It takes two arguments:

 - `name` - name of a new file,
 - `ftype` - type of a new file, must be `FileType` enum value:
     - `FileType.file`
     - `FileType.dir` or `FileType.directory`

For example, let's create an empty config
for some Forge mod, I'll call it "testmod".
```python
# Import enum
from python_aternos import FileType

# Get configs directory
conf = fm.get_file('/config')

# Create empty file
conf.create('testmod.toml', FileType.file)
```

### Editing files
Let's edit `ops.json`.
It contains operators nicknames,
so the code below is the same as [Players API](../players/#list-types).

```python
import json
from python_aternos import Client

at = Client.from_credentials('username', 'password')
serv = at.list_servers()[0]

fm = serv.files()
ops = fm.get_file('/ops.json')

# If editable
use_get_text = True

# Check
if not ops.editable:

    # One more check
    if not ops.downloadable:
        print('Error')
        exit(0)

    # If downloadable
    use_get_text = False

def read():

    if use_get_text:
        return ops.get_text()
    else:
        return ops.get_content().decode('utf-8')

def write(content):

    # set_text and set_content
    # uses the same URLs,
    # so there's no point in checking
    # if the file is editable/downloadable

    # Code for set_text:
    #ops.set_text(content)

    # Code for set_content:
    # Convert the str to bytes
    content = content.encode('utf-8')
    # Edit
    ops.set_content(content)

# ops.json contains an empty list [] by default
oper_raw = read()

# Convert it to a Python list
oper_lst = json.loads(oper_raw)

# Add an operator
oper_lst.append('DarkCat09')

# Convert back to JSON
oper_new = json.dumps(oper_lst)

# Write
ops.write(oper_new)
```
