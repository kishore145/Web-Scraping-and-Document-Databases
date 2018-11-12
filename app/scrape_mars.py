from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


def scrape():

    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = news_mars(browser)

    # Run all scraping functions and store in dictionary.
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }
    print(f'Scraped Data: {data}')
    # Stop webdriver and return data
    browser.quit()
    return data


def news_mars(browser):
    # Visit the mars nasa news site using the url provided in the readme
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    try:
        # using chrome dev tools, inspect the article header and find the element
        news_list = soup.find('ul', class_='item_list')
        latest_news = news_list.find("li", class_= 'slide')
        # Use the parent element to find the first a tag and save it as `news_title`
        news_title = latest_news.find('div', class_= 'content_title').get_text()
        print(news_title)
        # Use the parent element to find the paragraph text
        news_p = latest_news.find('div', class_="article_teaser_body").get_text()
        print(news_p)
    except AttributeError:
        return None, None
    
    print(f'News_mars ran successfully')
    print(f'News Title: {news_title}')
    print(f'News Teaser: {news_p}')

    return news_title, news_p


def featured_image(browser):
    # Visit URL for JPL Featured Space Image here.
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    # Use splinter to navigate the site and find the image url for the current Featured Mars Image and assign the url string to a variable called featured_image_url
    # id of the button is 'full_image'
    full_image_button = browser.find_by_id('full_image')
    full_image_button.click()
    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_button = browser.find_link_by_partial_text('more info')
    more_info_button.click()
    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')
    
    try:
        # find the relative image url
        img_url_rel = img_soup.find('figure', class_= 'lede').find('a')['href']
        print(img_url_rel)
        # Use the base url to create an absolute url from the example text provided in readme
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
        print(img_url)
    except AttributeError:
        return None

    print(f'Image URLs: {img_url}')
    return img_url


def hemispheres(browser):

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemisphere_image_urls = []

    # First, get a list of all of the hemispheres
    links = browser.find_by_css("a.product-item h3")

    # Next, loop through those links, click the link, find the sample anchor, return the href
    for i in range(len(links)):
        hemisphere = {}
    
        # We have to find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item h3")[i].click()
        try:
            # Next, we find the Sample image anchor tag and extract the href
            sample_elem = browser.find_link_by_text('Sample').first
            hemisphere['img_url'] = sample_elem['href']
            # Get Hemisphere title
            hemisphere['title'] = browser.find_by_css("h2.title").text
        
        except AttributeError:
            hemisphere['img_url'] = None
            hemisphere['title'] = None

    
        # Append hemisphere object to list
        hemisphere_image_urls.append(hemisphere)
    
        # Finally, we navigate backwards
        browser.back()

    print(f'Hemisphere Image URLs: {hemisphere_image_urls}')
    return hemisphere_image_urls


def twitter_weather(browser):
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)

    html = browser.html
    weather_soup = BeautifulSoup(html, 'html.parser')
    try: 
        # First, find a tweet 
        mars_weather_tweet = weather_soup.find('div', class_='js-tweet-text-container')
        # Next, search within the tweet for the p tag containing the tweet text
        mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()
    except:
        mars_weather = None
    
    print(f'Mars weather: {mars_weather}')

    return mars_weather


def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    df.columns=['Description', 'Value']
    
    print(df)
    # Add some bootstrap styling to <table>
    return df.to_html(classes="table table-striped", index=False)


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape())
