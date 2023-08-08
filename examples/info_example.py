from getpass import getpass

from selenium.webdriver import Firefox
from python_aternos import Client

user = input('Username: ')
pswd = getpass('Password: ')

driver = Firefox()

atclient = Client(driver)
atclient.login(user, pswd)

driver.quit()
