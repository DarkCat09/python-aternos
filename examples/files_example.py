from getpass import getpass
from python_aternos import Client

user = input('Username: ')
pswd = getpass('Password: ')

atclient = Client()
aternos = atclient.account
atclient.login(user, pswd)

s = aternos.list_servers()[0]
files = s.files()

while True:

    inp = input('> ').strip()
    cmd = inp.lower()

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
        path = inp[4:].strip()
        directory = files.list_dir(path)

        print(path, 'contains:')
        for file in directory:
            print('\t' + file.name)

    if cmd == 'world':
        file_w = files.get_file('/world')

        if file_w is None:
            print('Cannot create /world directory object')
            continue

        with open('world.zip', 'wb') as f:
            f.write(file_w.get_content())
