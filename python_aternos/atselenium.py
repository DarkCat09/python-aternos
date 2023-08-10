from selenium.webdriver import Remote
from selenium.webdriver.support.wait import WebDriverWait


BASE_URL = 'https://aternos.org'

RM_SCRIPTS = '''
const rmScripts = () => {
    const lst = document.querySelectorAll("script")
    for (let js of lst) {
        if (
            js.src.includes('googletagmanager.com') ||
            js.src.includes('cloudflareinsights.com') ||
            js.innerText.includes('LANGUAGE_VARIABLES')
        ) {
            js.remove()
        }
    }
}
addEventListener('DOMContentLoaded', rmScripts)
rmScripts()
'''


class SeleniumHelper:

    def __init__(self, driver: Remote) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, 8.0)
        self.find_element = self.driver.find_element
        self.find_elements = self.driver.find_elements

    def load_page(self, path: str) -> None:
        self.driver.get(f'{BASE_URL}{path}')
        self.driver.execute_script(RM_SCRIPTS)
    
    def exec_js(self, script: str) -> None:
        self.driver.execute_script(script)
    
    def get_cookie(self, name: str) -> str:
        cookie = self.driver.get_cookie(name)
        if cookie is None:
            return ''
        return cookie.get('value') or ''
    
    def set_cookie(self, name: str, value: str) -> None:
        self.driver.add_cookie({
            'name': name,
            'value': value,
        })
