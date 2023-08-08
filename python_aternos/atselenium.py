from selenium.webdriver import Remote
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


BASE_URL = 'https://aternos.org'

RM_SCRIPTS = '''
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
'''


class SeleniumHelper:

    def __init__(self, driver: Remote) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, 2.0)

    def load_page(self, path: str) -> None:
        self.driver.get(f'{BASE_URL}{path}')
        self.driver.execute_script(RM_SCRIPTS)

    def find_by_id(self, value: str) -> WebElement:
        return self.driver.find_element(By.ID, value)
    
    def find_by_class(self, value: str) -> WebElement:
        return self.driver.find_element(By.CLASS_NAME, value)
    
    def exec_js(self, script: str) -> None:
        self.driver.execute_script(script)
