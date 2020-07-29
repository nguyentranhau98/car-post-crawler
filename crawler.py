from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import urllib
import time
import requests
import json

options = Options()
options.set_headless()
browser = webdriver.Firefox(options=options)

browser.get('https://www.cars.com/shopping/')

container = browser.find_element_by_xpath("//section[@id='research-browseby']")
div_browse_makes = container.find_element_by_xpath("//div[@class='browse-makes']")
brands = div_browse_makes.find_elements_by_xpath("//li[@class='col-dt-4']")

list_link = []

print("Getting brands...")
for brand in brands:
    text = brand.find_element_by_css_selector('a').get_attribute('innerHTML')
    link = brand.find_element_by_css_selector('a').get_attribute('href')
    list_link.append((link, text))
    # print((link, text))
print("Finish getting brands...")





for link, text in list_link:
    no_car = 0
    car_dict = {}
    brand = text
    print("Crawling ", text, " at", link)
    browser.get(link)

    div_pages = browser.find_elements_by_xpath("//ul[@class='page-list']/li")[-1]
    max_page = div_pages.find_element_by_css_selector('a').get_attribute('innerHTML')

    for index in range(int(max_page)):
        # print("Moving to next page")
        page_url = link + "?page=" + str(index + 1)
        print(page_url)
        browser.get(page_url)
        div_posts = browser.find_elements_by_xpath("//div[@class='shop-srp-listings__listing-container']/a[@class='shop-srp-listings__listing']")
        if not div_posts:
            out_file = open("./"+brand+".json", "w")
            continue
        print("Crawling from page", index + 1)
        print("Start getting posts...")
        post_details_urls = []
        for div_post in div_posts:
            post_details_url = div_post.get_attribute('href')
            post_details_urls.append(post_details_url)
            
        for post_url in post_details_urls:
            if 'www.cars.com' in post_url:
                browser.get(post_url)
                wait = WebDriverWait(browser, 5)
                checked = False
                while(not checked):
                    try:
                        print("Trying....")
                        browser.save_screenshot("./sele.png")
                        element = wait.until(EC.presence_of_element_located((By.ID, 'vdpe-leadform')))
                        checked = True
                    except:
                        browser.get(post_url)
                
                car_model = browser.find_element_by_xpath("//section/div/div/h1[@class='cui-heading-2--secondary vehicle-info__title']").get_attribute('innerHTML')
                price = browser.find_element_by_xpath("//section/div/div/span[@class='vehicle-info__price-display vehicle-info__price-display--dealer cui-heading-2']").get_attribute('innerHTML')
                
                print("Start getting images...")
                img_dict = {}
                images = browser.find_elements_by_xpath("//div[@class='gallery-controls__thumbnail-image']")
                img_count = 0
                for image in images:
                    img_count += 1
                    img_dict['image_' + str(img_count)] = image.get_attribute('data-image')
                print("Finish getting images...")

                print("Start getting information...")
                info_dict = {}
                other_feature = []
                basic_specs = browser.find_elements_by_xpath("//li[@class='vdp-details-basics__item']/strong")
                basic_specs_values = browser.find_elements_by_xpath("//li[@class='vdp-details-basics__item']/span")
                other_infos = browser.find_elements_by_xpath("//li[@class='details-feature-list__item']")
                try:
                    for i in range(len(basic_specs)):
                        info_dict[basic_specs[i].get_attribute('innerHTML')] = basic_specs_values[i].get_attribute('innerHTML')
                    for j in range(len(other_infos)):
                        other_feature.append(other_infos[j].get_attribute('innerHTML'))
                    info_dict['other_features'] = other_feature
                except:
                    continue
                print("Finish getting information...")

                car2json = {}
                car2json["brand"] = brand
                car2json["model_version"] = car_model
                car2json["price"] = price
                car2json["information"] = info_dict
                car2json["img_urls"] = img_dict
                car_dict[no_car] = car2json
                no_car += 1
                out_file = open("./"+brand+".json", "w")
                json.dump(car_dict, out_file, indent=4)
                print("Got model:", car_model)

        print("Finish getting posts...")

        


