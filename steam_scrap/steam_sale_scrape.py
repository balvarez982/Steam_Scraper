"""
File: steam_sale_scrape.py
Author: Brandon Alvarez
Date: 1/29/2023
Description:

TODO:
    - Handle case where the results are filtered (Completed)
    - Handle case where there are more than 50 results and the results are paginated (In Progress)
        - To Decide: We should only do the first 50 results, intended to wishlist not for general search
"""
from bs4 import BeautifulSoup
import requests

#class to hold the data of the web scraping results
#takes into input the thumbnail, title, discount percent, and price comparison between original and discounted price
class SteamSaleScraper:

    def __init__(self, thumbnail, title, discount, price_compare):
        self.thumbnail = thumbnail
        self.title = title
        self.discount = discount
        self.price_compare = price_compare

    def getThumbnail(self):
        return self.thumbnail
    
    def getTitle(self):
        return self.title
    
    def getDiscount(self):
        return self.discount
    
    def getPriceCompare(self):
        return self.price_compare

def generateUrl(left, right, title):
    url = left + title + right
    return url

def searchTitle(title):
    # title = "Elder Scrolls V: Skyrim" -> "Elder+Scrolls+V+Skyrim". For simplicity, drop any special characters
    for char in title:
        if not char.isalnum():
            title.replace(char, "")
    title = title.replace(" ", "+")

    #construct url
    url = generateUrl("https://store.steampowered.com/search/?term=", "&force_infinite=1&specials=1&ndl=1", title)

    #generateUrl returns a list of urls, search title only needs one url and for search title
    #generateUrl will only return a urlList with one element, so simply return the first element
    return(url)

def initialScrape(url, title):
    #parse html of entire page given the url
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")

    #find the div with the id "search_results" and capture its body
    specials = soup.find(id='search_results')

    return specials
    
def numResults(count):

    #taking in the number of results from the search, and returning the text of the result class
    #in the case where the results are filtered, the following acts as "or"
    result = count.find(class_=["search_results_count", "search_results_filtered_warning"]).text

    result = result.strip().split(".", 1)[0] + "."

    return result

def getSearchResults(results, name, tag):
    element = results.find_all(tag, class_=name)
    return(element)

def deconstructResultList(array, tag):

    if tag:
        result = []
        for elem in array:
            result.append(elem[tag])
        return result
    result = []
    for elem in array:
        result.append(elem.text.strip())

    return result

def seperateOriginalFromDiscountedPrice(array):
    
    result = []
    for combo in array:
        combo = combo.split("$", 2)
        result.append(combo[1:3])

    for i, pair in enumerate(result):
        for j, price in enumerate(pair):
            price = "$"+price
            result[i][j] = price

    return result

def createSteamSaleScraperObject(thumbnail, title, discount, price_compare):
    return SteamSaleScraper(thumbnail, title, discount, price_compare)

def generateSearchResults(search):
    #get the unformatted stream of the resulting elements
    images = getSearchResults(search, None, "img")
    titles = getSearchResults(search,"title", None)
    discounts = getSearchResults(search, "col search_discount responsive_secondrow", None)
    price = getSearchResults(search, "col search_price discounted responsive_secondrow", None)

    #get the raw stream of the text values of the resulting elements
    #strip leading and following whitespaces and newlines
    images_raw = deconstructResultList(images, "src")
    titles_raw = deconstructResultList(titles, None)
    discounts_raw = deconstructResultList(discounts, None)

    #prices_raw is structered as [original pricediscounted price], convert to [[original price, discounted price]]
    price_raw = deconstructResultList(price, None)
    price_formatted = seperateOriginalFromDiscountedPrice(price_raw)

    results = []
    #doesnt matter what we iterate over, they all have the same length
    for i in range(len(images_raw)):
        results.append(createSteamSaleScraperObject(images_raw[i], titles_raw[i], discounts_raw[i], price_formatted[i]))
    return results

def titleMatching(search, results):
    #compare the search term to the titles of the results and pop any value that doesn't compare well enough
    #in order to validate that the results are actually for the game we are searching for
    return results

def main():

    search = "RPG"
    url = searchTitle(search)

    specials = initialScrape(url, search)

    # if type(specials) == 'list':
    #     test = open("large_test4.txt", "a")
    #     for result in specials:
    #         test.write(result.prettify())
    #     test.close()
    # else:
    #     test = open("large_test3.txt", "w")
    #     test.write(specials.prettify())
    #     test.close()

    numOfSpecials = numResults(specials)
    print(numOfSpecials)

    if numOfSpecials[0] != "0":
        result = generateSearchResults(specials)
        count = 0
        #tester
        for obj in result:
            count += 1
            print(obj.getThumbnail())
            print(obj.getTitle())
            print(obj.getDiscount())
            print(obj.getPriceCompare())
            print()
        print(count)

main()
