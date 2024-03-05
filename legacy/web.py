from flask import Flask, render_template
from scrape import reloadPageRaw
from scrape import updateProductFile
import concurrent.futures
import os
import time

HOST_BIND = "0.0.0.0"
HOST_PORT = 20202
REMOTE = False #Remote into docker container for browser env?
batchSize = 4

app = Flask(__name__)

topDir = os.getcwd()[len(os.path.dirname(os.getcwd()))+1:] #Get current dir
dataDir = os.path.join("Test Web Scraping", "PyElkScrape", "data") if topDir == "Python Stuff" else "data"
blackListFile = os.path.join(dataDir, "blacklist.txt")

blacklistedItems = []
pages = ["https://www.elkjop.no/outlet/page-1?filter=BGradeTitle:Som%20ny%20-%20Utg%C3%A5tt%20fra%20butikksortiment&sort=ActivePrice.Amount:desc"]

lastRawProds = []
lastTime = 0

def containBlacklist(prodName):

    for s in blacklistedItems:
        if s.lower() in prodName.lower():
            return True

    return False

# def browsePages(webURL, pages):

#     dat = []

#     for currentPage in webURL:
#         for batch in range(0, pages, batchSize):

#             with concurrent.futures.ThreadPoolExecutor() as exec:
#                 futures = [exec.submit(reloadPageAndFilter, REMOTE, blacklistedItems, currentPage.replace("page-1?", f"page-{i+batch+1}?")) for i in range(batchSize if batch+batchSize < pages else pages-batch)]
#                 concurrent.futures.wait(futures)
                
#                 for f in futures:
#                     dat.append(f.result())


#     return dat

def browsePagesRaw(webURL, pages):

    dat = []

    for currentPage in webURL:
        for batch in range(0, pages, batchSize):

            with concurrent.futures.ThreadPoolExecutor() as exec:
                futures = [exec.submit(reloadPageRaw, REMOTE, currentPage.replace("page-1?", f"page-{i+batch+1}?")) for i in range(batchSize if batch+batchSize < pages else pages-batch)]
                concurrent.futures.wait(futures)
                
                for f in futures:
                    dat.append(f.result())

    return dat

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
