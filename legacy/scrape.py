from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os


topDir = os.getcwd()[len(os.path.dirname(os.getcwd()))+1:] #Get current dir
dataDir = os.path.join("Test Web Scraping", "PyElkScrape", "data") if topDir == "Python Stuff" else "data"
driverDir = os.path.join("Test Web Scraping", "PyElkScrape", "drivers") if topDir == "Python Stuff" else "drivers"

firefoxInstallPath = r"c:\Program Files\Mozilla Firefox\firefox.exe"

csvProductFile = os.path.join(dataDir, "products.csv")
blackListFile = os.path.join(dataDir, "blacklist.txt")
firefoxDriver = os.path.join(driverDir, "geckodriver.exe")
phantomDriver = os.path.join(driverDir, "phantomjs.exe")

print(csvProductFile)
print(blackListFile)
print(firefoxDriver)
print(phantomDriver)

def createFirefoxBrowserEnv():
    opt = webdriver.FirefoxOptions()
    opt.binary_location = firefoxInstallPath
    opt.add_argument("--headless")

    browser = webdriver.Firefox(executable_path=firefoxDriver, options=opt)
    return browser

def createPhantomBrowserEnv(): #Doesnt work

    webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
    browser = webdriver.PhantomJS(executable_path=phantomDriver)
    
    return browser

def createRemoteChromeEnv():

    opt = webdriver.ChromeOptions()
    browser = webdriver.Remote("http://192.168.50.57:4444", options=opt)

    return browser

def navigateToPage(browser, webURL):
    browser.get(webURL)

def waitForCookiePopup(browser):
    try:
        cookieButtonXPath = r'//*[@id="coiPage-1"]/div[2]/button[2]'
        wait = WebDriverWait(browser, 20)
        waitForElement = wait.until(EC.presence_of_element_located((By.XPATH, cookieButtonXPath)))
    except:
        return

def clickCookiePopup(browser:webdriver.Remote):

    try:
        cookieButtonXPath = r'//*[@id="coiPage-1"]/div[2]/button[2]'
        cookieButton = browser.find_element(By.XPATH, cookieButtonXPath)

        cookieButton.click()
    
        return True
    except:
        return False

def waitForNextButton(browser):
    el = r'//*[@id="products"]/elk-component-loader-wrapper/elk-product-and-content-listing-view/div[2]/elk-pagination/div/div[1]/a'
    wait = WebDriverWait(browser, 20)
    try:
        waitForElement = wait.until(EC.presence_of_element_located((By.XPATH, el)))
    except:
        print("Timeout")

def scrollToBottom(browser):

    i = 0
    while i <= 10:

        i += 1
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        if len(getProductElements(browser)) >= 48:
            return
        
        time.sleep(.25)

def getProductElements(browser):

    productElements = browser.find_elements(By.TAG_NAME, "elk-product-tile")
    #print("Products found: {}".format(len(productElements)))
    
    return productElements

def getDisplayProducts(browser):

    productsDisplay = []

    for pe in getProductElements(browser):

        try: 
            titleDiv = pe.find_element(By.TAG_NAME, "div")

            productLink = titleDiv.find_element(By.TAG_NAME, "a").get_property("href")
            productTitle = titleDiv.get_property("title").strip()

            productInfoParent = titleDiv.find_element(By.CLASS_NAME, "product-tile__information")
            productInfo_Price = productInfoParent.find_element(By.TAG_NAME, "elk-price")
            productNewPrice = productInfo_Price.find_element(By.CLASS_NAME, "ng-star-inserted").text[0:-2]

            productImg = titleDiv.find_element(By.CLASS_NAME, "product-tile__image").get_property("src")
            
            product = [productTitle, productNewPrice, productLink, productImg]
            productsDisplay.append(product)
        except:
            donothing = ""
    
    return productsDisplay

def waitForFileAccess():

    while True:
        try:
            with open(csvProductFile, "r", newline=''):
                pass
            return True
        except IOError:
            time.sleep(.25)

    return False #Should never happen


def saveProductsToFile(prods):

    waitForFileAccess()
    f = open(csvProductFile, "w", newline='')
    cw = csv.writer(f)
    cw.writerows(prods)
    
    f.close()

def readProductFile():
    
    dat = []

    waitForFileAccess()
    f = open(csvProductFile, "r", newline='')
    cr = csv.reader(f)

    for l in cr:
        dat.append(l)

    f.close()

    return dat

def updateProductFile(prods):

    oldProds = readProductFile() if os.path.exists(csvProductFile) else []

    for p in prods:
        if not p in oldProds:
            print(f"New product: {p[0]}")
            oldProds.append(p)
    saveProductsToFile(oldProds)

    return True

def containBlacklist(blacklistedItems, prodName):

    for s in blacklistedItems:
        if s.lower() in prodName.lower():
            return True
        
    return False

def reloadPageAndFilter(remote, blacklistedItems, webURL):

    #print(webURL)
    browser = createRemoteChromeEnv() if remote else createFirefoxBrowserEnv()
    try:
        navigateToPage(browser, webURL)
        waitForCookiePopup(browser)
        flag = clickCookiePopup(browser)
        waitForNextButton(browser)
        scrollToBottom(browser)

        rawProds = getDisplayProducts(browser)
        prods = []
    
        for prod in rawProds:
            if not containBlacklist(blacklistedItems, prod[0]):
                prods.append(prod)

        print(f"Products found: {len(prods)} ({len(rawProds)})")
    finally:
        browser.quit()

    return prods

def reloadPageRaw(remote, webURL):

    #print(webURL)
    browser = createRemoteChromeEnv() if remote else createFirefoxBrowserEnv()
    try:
        navigateToPage(browser, webURL)
        waitForCookiePopup(browser)
        flag = clickCookiePopup(browser)
        waitForNextButton(browser)
        scrollToBottom(browser)
        
        rawProds = getDisplayProducts(browser)
        print(f"Products found: {len(rawProds)}")
    finally:
        browser.quit()

    return rawProds