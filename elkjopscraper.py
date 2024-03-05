from elkjopworker import ElkWorker
from selenium.webdriver.common.by import By
from datetime import datetime

class ElkScraper:

    def __init__(self, weburl:str, runPath:str, remoteWorker:bool=False, driverPath:str=None, timesToBottom:int=10, expectedProdCount:int=48):
        try:
            self.ew = ElkWorker(weburl, runPath, remoteWorker, driverPath, timesToBottom, expectedProdCount)
            self.products = self.__populateProducts__() #This takes a long time -- Possible to fix?
        finally:
            self.ew.browser.quit()

    def __populateProducts__(self):
        """Returns [[productTitle, productNewPrice, productLink, productImg, datetime(YYYY/MM/DD HH:MM:SS)]]"""

        prods = []
        for pe in self.ew.getHtmlProducts():

            try: 
                titleDiv = pe.find_element(By.TAG_NAME, "div")

                productLink = titleDiv.find_element(By.TAG_NAME, "a").get_property("href")
                productTitle = titleDiv.get_property("title").strip()

                productInfoParent = titleDiv.find_element(By.CLASS_NAME, "product-tile__information")
                productInfo_Price = productInfoParent.find_element(By.TAG_NAME, "elk-price")
                productNewPrice = productInfo_Price.find_element(By.CLASS_NAME, "ng-star-inserted").text[0:-2]

                productImg = titleDiv.find_element(By.CLASS_NAME, "product-tile__image").get_property("src")
                
                product = [productTitle, productNewPrice, productLink, productImg, datetime.now().strftime("%Y/%m/%d %H:%M:%S")]
                prods.append(product)
            except:
                print("Something went wrong in the product parsing")
                
        return prods

    def getProducts(self):
        """Returns [[productTitle, productNewPrice, productLink, productImg, datetime(YYYY/MM/DD HH:MM:SS)]]"""

        return self.products