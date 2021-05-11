# Dependencies
import pandas as pd
from pprint import pprint
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from pymongo import MongoClient
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import time
from pprint import pprint

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 

# Create function to scrape all data needed for site then inserting the data into MongoDB
def scrape():

    ######## NASA Mars News ########
    # Set up Spinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    
    # Create the soup 
    html = browser.html
    soup = bs(html, 'html.parser')

    # Grab latest news title
    title = soup.find_all('div',class_='content_title')
    news_title = title[1].text.strip()
    #news_title

    # Grab latest news title's paragraph text
    p = soup.find_all('div',class_='article_teaser_body')
    news_p = p[1].text.strip()
    #news_p

    # Quit browser session
    browser.quit()



    ######## JPL Mars Space Images - Featured Image ########
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    # Grab url for the current Featured Mars Image
    featured_url ='https://www.jpl.nasa.gov/images?search=&category=Mars'
    browser.visit(featured_url)

    # Clicking the Mars checkbox button
    target = 'input[class="text-theme-red focus:ring-2 focus:ring-jpl-red flex-shrink-0 w-5 h-5 mt-px mr-1 align-middle border rounded-none"]'
    browser.find_by_tag(target).click()

    # Clicking the Mars image
    target = 'a[class="group  cursor-pointer block"]'
    browser.find_by_tag(target).click()

    #Pauses for a few seconds 
    time.sleep(3)

    # Create the soup 
    html = browser.html
    soup = bs(html,'html.parser')

    # Grab full-size image url
    featured_image_url = soup.find_all('a', class_="BaseButton")[0]['href']
    #featured_image_url

    # Quit browser session
    browser.quit()



    ######## Mars Facts #########
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    # Grab facts url to scrape Mars data using Pandas
    facts_url = 'https://space-facts.com/mars/'

    # Using Pandas to scrape the mars facts table
    facts_table = pd.read_html(facts_url)[0]
    #facts_table

    # Add column names to table
    facts_table.columns = ['Description','Value']
    #facts_table

    # Use Pandas to convert the data to a HTML table string
    facts_html = facts_table.to_html()
    #facts_html 

    # Replace every '\n' in the HTML string with blank spaces
    facts_html_string = facts_html.replace('\n', '')
    #facts_html_string

    # Quit browser session
    browser.quit()



    ######## Mars Hemispheres ########
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    # URL for Hemispheres site
    hem_url ="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hem_url)

    # Create the soup 
    html = browser.html
    soup = bs(html,'html.parser')  

    # Get the hemisphere html
    hem_html = soup.find_all('div', class_="description")
    #hem_html

    # Create empty dictionary to store Hemisphere Info
    hem_img_urls = []

    # Loop through headers to grab the title and image URL for each hemisphere and put into 
    for x in range(len(hem_html)):
        img_dict = {}
        ref = hem_html[x].h3.text
        browser.find_by_text(ref).click()
    
        html = browser.html
        soup = bs(html,'html.parser')
    
        img = soup.find_all('div', class_="downloads")
        img_url = img[0].li.a['href']
    
        titles = soup.find_all('h2',class_="title")
        title = titles[0].text
    
        img_dict = {"title":title,"img_url":img_url}
        hem_img_urls.append(img_dict)
    
        browser.back()

    # List of dictionaries for each hemisphere
    hem_img_urls
 
    # Quit browser session
    browser.quit()

    
    # Create dictionary
    mars_info = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "facts_html_string": facts_html_string,
        "hem_img_urls": hem_img_urls
        
    }


    collection.insert(mars_info)
    return mars_info

#scrape()





