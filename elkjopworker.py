from browserworker import BrowserWorker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ElkWorker(BrowserWorker):

    def __init__(self, weburl:str, runPath:str, remoteWorker:bool=False, driverPath:str=None, timesToBottom:int=10, expectedProdCount:int=48):
        super().__init__(weburl, runPath, remoteWorker, driverPath, timesToBottom, expectedProdCount)
        

    def waitForCookiePopup(self):
        try:
            cookieButtonXPath = r'//*[@id="coiPage-1"]/div[2]/button[2]'
            wait = WebDriverWait(self.browser, 20)
            waitForElement = wait.until(EC.presence_of_element_located((By.XPATH, cookieButtonXPath)))
        except:
            return
    

    def clickCookiePopup(self):
        try:
            cookieButtonXPath = r'//*[@id="coiPage-1"]/div[2]/button[2]'
            cookieButton = self.browser.find_element(By.XPATH, cookieButtonXPath)

            cookieButton.click()
        
            return True
        except:
            return False


    def waitForPageToPopulate(self):
        el = r'//*[@id="products"]/elk-component-loader-wrapper/elk-product-and-content-listing-view/div[2]/elk-pagination/div/div[1]/a'
        wait = WebDriverWait(self.browser, 20)
        try:
            waitForElement = wait.until(EC.presence_of_element_located((By.XPATH, el)))
        except:
            print("Timeout")
    

    def getHtmlProducts(self):
        return self.browser.find_elements(By.TAG_NAME, "elk-product-tile")