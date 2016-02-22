import sys
import os
wd = os.path.abspath('.')
sys.path.append(wd + '/../')
import random
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from general_utilities.navigation_utilities import issue_driver_query
from general_utilities.parsing_utilities import parse_num

def scrape_job_page(driver, job_title, job_location):
    """Scrape a page of jobs from Glassdoor. 

    Here, we'll grab everything that we can (or is relevant) for each 
    of the jobs posted for a given page. This will include the job title, 
    the job location, the posting company, the date posted, and then any 
    stars assigned (if any).

    Args: 
        driver: Selenium webdriver
        job_title: str
        job_location: str
    """
    
    current_date = datetime.date.today().strftime("%m-%d-%Y")
    json_dct = {'search_title': job_title, \
            'search_location': job_location, \
            'search_date': current_date}

    jobs = driver.find_elements_by_class_name('jobListing')
    for job in jobs: 
        query_for_data(driver, json_dct, job)

def query_for_data(driver, json_dct, job): 
    """Grab all info. from the job posting
    
    This will include the job title, the job location, the 
    posting company, the date posted, and then any stars assigned 
    (if any). We'll also then click and get the job postings 
    actual text. 

    Args: 
        driver: Selenium webdriver
        json_dct: dict 
            Dictionary holding the current information we're storing for 
            that job posting. 
        job: Selenium element
    """

    posting_title = job.find_element_by_class_name('title').text
    split_posting_company = job.find_element_by_class_name(
            'companyInfo').text.split()
    posting_location = job.find_element_by_xpath(
            "//div//span[@itemprop='jobLocation']").text
    posting_date = job.find_element_by_class_name('minor').text

    # I couldn't think of any clearly better way to do this. If they have 
    # a number of stars, it comes in the posting companies text. I guess
    # I could have done a search and replace, but I'd rather slightly adjust
    # some functionality I already have (i.e. parse_num) than build another
    # function to find the number of stars, store it, and then replace it with
    # empty text. 
    if parse_num(' '.join(split_posting_company), 0):
        num_stars = split_posting_company[0]
        posting_company = ' '.join(split_posting_company[1:])
        gen_output(json_dct, posting_title, posting_location, posting_date,
                posting_company, num_stars)
    else: 
        posting_company = ' '.join(split_posting_company)
        gen_output(json_dct, posting_title, posting_location, posting_date,
                posting_company)

def gen_output(json_dct, *args): 
    """
    """
    pass

if __name__ == '__main__':
    # I expect that at the very least a job title and job location
    # will be passed in, so I'll attempt to get both of those within
    # a try except and throw an error otherwise. 
    try: 
        job_title = sys.argv[1]
        job_location = sys.argv[2]
    except IndexError: 
        raise Exception('Program needs a job title and job location inputted!')
    
    # Issue the job query. 
    base_URL = 'https://www.glassdoor.com/index.htm'
    query_params = (('KeywordSearch', job_title), 
            ('LocationSearch', job_location))
    driver = issue_driver_query(base_URL, query_params)

    # Find the text holding the number of jobs, and parse it. 
    time.sleep(random.randint(7, 15))
    num_jobs_txt = driver.find_elements_by_xpath('//header')[1].text
    num_jobs = int(parse_num(num_jobs_txt, 0)) 
    
    # Find the text holding the number of pages in the job search. 
    time.sleep(random.randint(2, 6))
    num_pages_txt = driver.find_element_by_id('ResultsFooter').text
    num_pages = int(parse_num(num_pages_txt, 1))

    # Find all the jobs. 
    time.sleep(random.randint(6, 12))
    job_listings = driver.find_elements_by_class_name('jobListing')

    jobs = scrape_job_page(driver, job_title, job_location)
