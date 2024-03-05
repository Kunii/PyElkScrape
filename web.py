from flask import Flask, render_template
from elkjopscraper import ElkScraper
import concurrent.futures
import os
import time
import csv

HOST_BIND = "0.0.0.0"
HOST_PORT = 20202
batchSize = 4

app = Flask(__name__)

topDir = os.getcwd()[len(os.path.dirname(os.getcwd()))+1:] #Get current dir
dataDir = os.path.join("Test Web Scraping", "PyElkScrape", "data") if topDir == "Python Stuff" else "data"
blackListFile = os.path.join(dataDir, "blacklist.txt")
csvProductFile = os.path.join(dataDir, "products.csv")

blacklistedItems = []
pages = ["https://www.elkjop.no/outlet/page-1?filter=BGradeTitle:Som%20ny%20-%20Utg%C3%A5tt%20fra%20butikksortiment&sort=ActivePrice.Amount:desc"]

lastRawProds = []
lastTime = 0

def containBlacklist(prodName):

    for s in blacklistedItems:
        if s.lower() in prodName.lower():
            return True

    return False

# driverDir = os.path.join("Test Web Scraping", "PyElkScrape", "drivers") if topDir == "Python Stuff" else "drivers"
# firefoxInstallPath = r"c:\Program Files\Mozilla Firefox\firefox.exe"
# firefoxDriver = os.path.join(driverDir, "geckodriver.exe")

def createElkRemoteScraper(weburl):
    # return ElkScraper(weburl, firefoxInstallPath, False, firefoxDriver).getProducts()
    return ElkScraper(weburl, "http://192.168.50.57:4444", True).getProducts() 

def browsePagesRaw(webURL, pages):

    dat = []

    for currentPage in webURL:
        for batch in range(0, pages, batchSize):

            with concurrent.futures.ThreadPoolExecutor() as exec:
                futures = [exec.submit(createElkRemoteScraper, currentPage.replace("page-1?", f"page-{i+batch+1}?")) for i in range(batchSize if batch+batchSize < pages else pages-batch)]
                concurrent.futures.wait(futures)
                
                for f in futures:
                    dat.append(f.result())

    return dat

def waitForFileAccess():

    if not os.path.exists(csvProductFile):
        with open(csvProductFile, "x") as f:
            pass
    
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

def reloadRaw(forceReload:bool):
    
    global lastRawProds
    global lastTime
    print("Fetching Products")
    
    deltaTime = time.time() - lastTime
    print(f"Time before refresh: {(10 * 60) - deltaTime}")
    if lastTime == 0 or (deltaTime > (10 * 60)) or forceReload:

        print("Reloading raw")
        lastRawProds = browsePagesRaw(pages, 20)
        lastTime = time.time()

        for l in lastRawProds:
            updateProductFile(l)

    prods = []

    for page in lastRawProds:
        for prod in page:
            prods.append(prod)

    return prods

@app.route('/')
def index():
    
    print("Showing index")
    global blacklistedItems
    blacklistedItems = []

    with open(blackListFile, "r", encoding="UTF-8") as f:
        for l in f:
            if l != '':
                blacklistedItems.append(l.strip())
    
    print("Blacklist loaded")
    
    rl = reloadRaw(False)
    prods = []

    for prod in rl:
        if not containBlacklist(prod[0]):
            prods.append(prod)
    
    print(f"Products loaded: {len(prods)}/{len(rl)}")
    
    return render_template("index.html", products=prods)

@app.route('/raw')
def raw():
    
    rl = reloadRaw(False)
    print(f"Products loaded: {len(rl)}")

    return render_template("index.html", products=rl)

@app.route('/reload')
def displayReloadRaw():
    
    rl = reloadRaw(True)
    print(f"Products loaded: {len(rl)}")

    return render_template("index.html", products=rl)


if __name__ == '__main__': 
    
    print("Starting Up")
    print(f"Working path: {os.getcwd()}")

    app.run(host=HOST_BIND, port=HOST_PORT)
    print("Exiting...")
