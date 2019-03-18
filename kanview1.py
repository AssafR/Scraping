from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
from tabulate import tabulate
import os
import json



def read_using_driver(url):
    # create a new Firefox session
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.get(url)
    python_button = driver.find_element_by_id('MainContent_uxLevel1_Agencies_uxAgencyBtn_33')  # FHSU
    python_button.click()  # click fhsu link
    soup_level1 = BeautifulSoup(driver.page_source, 'lxml')

    datalist = []  # empty list

    x = 0  # counter
    for link in soup_level1.find_all('a', id=re.compile("^MainContent_uxLevel2_JobTitles_uxJobTitleBtn_")):
        print(link)
        # Selenium visits each Job Title page
        python_button = driver.find_element_by_id('MainContent_uxLevel2_JobTitles_uxJobTitleBtn_' + str(x))
        python_button.click()  # click link

        # Selenium hands of the source of the specific job page to Beautiful Soup
        soup_level2 = BeautifulSoup(driver.page_source, 'lxml')

        # Beautiful Soup grabs the HTML table on the page
        table = soup_level2.find_all('table')[0]

        # Giving the HTML table to pandas to put in a dataframe object
        df = pd.read_html(str(table), header=0)

        # Store the dataframe in a list
        datalist.append(df[0])

        # Ask Selenium to click the back button
        driver.execute_script("window.history.go(-1)")

        # increment the counter variable before starting the loop over
        x += 1
        if x > 2:
            break
    # end the Selenium browser session
    driver.quit()
    return datalist


def write_json_to_file(json_file_name):
    path = os.getcwd()
    # open, write, and close the file
    with open(path + os.path.sep + json_file_name , "w") as f:  # FHSU
        d = json.loads(json_records)
        f.write(json.dumps(d, indent=4))


def get_json_dataframe(datalist):
    # combine all pandas dataframes in the list into one big dataframe
    result = pd.concat([pd.DataFrame(datalist[i]) for i in range(len(datalist))], ignore_index=True)
    # convert the pandas dataframe to JSON
    json_records: str = result.to_json(orient='records')
    return result, json_records


#launch url
url = "http://kanview.ks.gov/PayRates/PayRates_Agency.aspx"
datalist = read_using_driver(url)
result, json_records = get_json_dataframe(datalist)

#pretty print to CLI with tabulate
#converts to an ascii table
print(tabulate(result, headers=["Employee Name","Job Title","Overtime Pay","Total Gross Pay"],tablefmt='psql'))

#get current working directory
write_json_to_file( "fhsu_payroll_data.json")

