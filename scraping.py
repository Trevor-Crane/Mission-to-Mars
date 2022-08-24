# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Set out news title and paragraph variables
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres" : mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Set up the HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
         # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p

### Featured Images

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        img_url_rel

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

### Mars Facts

def mars_facts():

    try:
        # Get Table from Mars Fact
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    #Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

### Mission to Mars Challenge, getting Hemisphere images

def mars_hemispheres(browser):
    # Visit the URL
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    try:
        #Create a list to hold the images and titles.
        hemisphere_image_urls = []

        #Find links for each hemisphere
        links = browser.find_by_css('a.product-item h3')

        #Loop through each link
        for items in range(4):
            #Click on each link
            browser.find_by_css('a.product-item h3')[items].click()
            hemisphere_data = scrape_hemisphere(browser.html)
            #Add both the url and title to our list
            hemisphere_image_urls.append(hemisphere_data)
            #Tell the browser to go back to rinse and repeat 
            browser.back()    
    except AttributeError:
        return None

    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    hemi_soup = soup(html_text, "html.parser")

    try:
        hemisphere_title = hemi_soup.find("h2", class_="title").get_text()
        hemisphere_sample = hemi_soup.find("a", text="Sample").get("href")
    except AttributeError:
        hemisphere_title = None
        hemisphere_sample = None
    
    hemisphere_dictionary = {
        "title": hemisphere_title,
        "img_url": hemisphere_sample
    }

    return hemisphere_dictionary

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())