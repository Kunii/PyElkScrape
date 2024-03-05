from selenium import webdriver
from abc import ABC, abstractmethod 
import time

class BrowserWorker(ABC):

    def __init__(self, weburl:str, runPath:str, remoteWorker:bool=False, driverPath:str=None, timesToBottom:int=10, expectedProdCount:int=48):
        self.url = weburl
        self.browser = self.createRemoteChromeEnv(runPath) if remoteWorker else self.createFirefoxBrowserEnv(runPath, driverPath)

        self.browser.get(weburl)

        self.waitForCookiePopup()
        self.clickCookiePopup()
        self.waitForPageToPopulate()
        self.scrollToBottom(timesToBottom, expectedProdCount)


    def createRemoteChromeEnv(self, remoteAddr):
        opt = webdriver.ChromeOptions()
        return webdriver.Remote(remoteAddr, options=opt)
    
    def createFirefoxBrowserEnv(self, firefoxExec, firefoxDriver):

        if firefoxDriver == None:
            raise Exception("Firefox driver path not provided")

        opt = webdriver.FirefoxOptions()
        opt.binary_location = firefoxExec
        opt.add_argument("--headless")

        return webdriver.Firefox(executable_path=firefoxDriver, options=opt)

    @abstractmethod
    def waitForCookiePopup(self):
        pass
    
    @abstractmethod
    def clickCookiePopup(self):
        pass

    @abstractmethod
    def waitForPageToPopulate(self):
        pass
    
    @abstractmethod
    def getHtmlProducts(self):
        pass

    def scrollToBottom(self, timesToBottom, expectedProdCount):
        
        for i in range(timesToBottom):
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            if len(self.getHtmlProducts()) >= expectedProdCount:
                return
            
            time.sleep(.25)

