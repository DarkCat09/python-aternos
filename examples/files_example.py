from getpass import getpass
from python_aternos import Client, atserver

user = input('Username: ')
pswd = getpass('Password: ')
aternos = Client.from_credentials(user, pswd)

s = aternos.list_servers()[0]
files = s.files()

while True:
    
    cmd = input('> ').strip().lower()

    if cmd == 'help':
        print(
            '''Commands list:
            help - show this message
            quit - exit from the script
            world - download the world
            list [path] - show directory (or root) contents'''
        )

    if cmd == 'quit':
        break

    if cmd.startswith('list'):
        path = cmd.removeprefix('list').strip()
        directory = files.listdir(path)

        print(path, 'contains:')
        for file in directory:
            print('\t' + file.name)
    
    if cmd == 'world':
        file = files.get_file('/world')
        with open('world.zip', 'wb') as f:
            f.write(file.get_content())
