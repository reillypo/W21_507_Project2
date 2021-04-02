#################################
##### Name: Reilly Potter
##### Uniqname: reillypo
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

BASEURL = 'https://www.nps.gov'

#set up cache
CACHEFILE = "cache.json"

def open_cache(CACHEFILE):
    try:
        with open(CACHEFILE,'r') as cache_file:
            cache_json = file.read()
            cache_diction = json.loads(cache_json)
    except:
        cache_diction = {}
    return cache_diction

def cache_data(CACHEFILE,url,cache_diction,new_data):
    with open(CACHEFILE,'w') as cache_file:
        cache_diction[url] = new_data
        cache_json = json.dumps(cache_diction)
        cache_file.write(cache_json)

cache_diction = open_cache(CACHEFILE)

# try to get the data out of the dictionary; if not, make a request to get it and then cache it
baseurl_data = cache_diction.get(BASEURL)
if not baseurl_data:
    baseurl_data = requests.get(BASEURL).text
    cache_data(CACHEFILE,BASEURL,cache_diction,baseurl_data)

#create BeautifulSoup object
soup = BeautifulSoup(baseurl_data, "html.parser")



class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        if category != '':
            self.category = category
        else:
            self.category = ''
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return f'{self.name} ({self.category}): {self.address} {self.zipcode}'



def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    state_sites_dict = {}
    # get the text of the class that contains the list of states in the dropdown and add each state to the database if it doesn't already exist
    dropdown = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    states_tags = dropdown.find_all('li')
    # print(states_tags)
    #iterate over each list item, find link and name.
    for tag in states_tags:
        url = tag.find('a')['href']
        name = tag.find('a').contents[0]
        state_sites_dict[name] = url
    # print(state_sites_dict)
    return state_sites_dict
       
# build_state_url_dict()

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    page_soup = BeautifulSoup(requests.get(site_url).text, 'html.parser')
    name = page_soup.find(class_='Hero-title').contents[0]
    category = page_soup.find(class_='Hero-designation').contents[0]
    address =  page_soup.find(itemprop="addressLocality").contents[0] + ', ' + page_soup.find(class_="region").contents[0]
    zipcode =  page_soup.find(class_="postal-code").contents[0]
    phone = page_soup.find(class_='tel').contents[0]

    site_instance = NationalSite(category, name, address, zipcode, phone)
    return site_instance

# get_site_instance('https://www.nps.gov/isro/index.htm')

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    national_site_inst_list = []
    state_soup = BeautifulSoup(requests.get(state_url).text, 'html.parser')
    all_site_link = state_soup.find_all(class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left')
    for link in all_site_link:
        park_link = link.find('a')['href']
        site_url = BASEURL + '/' + park_link + '/' + 'index.htm'
        national_site_inst_list.append(get_site_instance(site_url))

    print(national_site_inst_list)
    return national_site_inst_list

get_sites_for_state('https://www.nps.gov/state/mi/index.htm')

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    pass
    

if __name__ == "__main__":
    pass