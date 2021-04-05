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
    ''' Opens the cache file if it exists and loads the JSON into
    the cache_diction dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    CACHEFILE: json file
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        with open(CACHEFILE,'r') as cache_file:
            cache_json = cache_file.read()
            cache_diction = json.loads(cache_json)
    except:
        cache_diction = {}
    return cache_diction

def cache_data(CACHEFILE,url,cache_diction,new_data):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_diction: dict
        The dictionary to save
    CACHEFILE: json
        The json file you'll populate
    url: str
        url of information you're caching
    new_data: dict
        information pulled from site
    
    Returns
    -------
    None
    '''
    with open(CACHEFILE,'w') as cache_file:
        cache_diction[url] = new_data
        cache_json = json.dumps(cache_diction)
        cache_file.write(cache_json)

cache_diction = open_cache(CACHEFILE)



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
    if BASEURL in cache_diction.keys():
        print("Using Cache")
        baseurl_data = cache_diction[BASEURL]
    else:
        print("Fetching")
        cache_diction[BASEURL] = requests.get(BASEURL).text
        baseurl_data = cache_diction[BASEURL]
        cache_data(CACHEFILE, BASEURL, cache_diction, baseurl_data)
    
    soup = BeautifulSoup(baseurl_data, "html.parser")

    state_sites_dict = {}
    # get the text of the class that contains the list of states in the dropdown and add each state to the database if it doesn't already exist
    dropdown = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    states_tags = dropdown.find_all('li')
    # print(states_tags)
    #iterate over each list item, find link and name.
    for tag in states_tags:
        url = tag.find('a')['href']
        full_url = BASEURL + url
        name = tag.find('a').contents[0]
        state_sites_dict[name.lower()] = full_url
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
    if site_url in cache_diction.keys():
        print("Using Cache")
        siteurl_data = cache_diction[site_url]
    else:
        print("Fetching")
        cache_diction[site_url] = requests.get(site_url).text
        siteurl_data = cache_diction[site_url]
        cache_data(CACHEFILE, site_url, cache_diction, siteurl_data)
    
    page_soup = BeautifulSoup(siteurl_data, 'html.parser')
    
    try:
        name = page_soup.find(class_='Hero-title').contents[0]
    except:
        name = "No name"
    try:
        category = page_soup.find(class_='Hero-designation').contents[0].strip(' ')
    except:
        category = "No category"
    try:
        city =  page_soup.find(itemprop="addressLocality").contents[0].strip(' ')#page_soup.find(class_="region").contents[0]
    except:
        city = "No city"
    try:
        state = page_soup.find(itemprop="addressRegion").contents[0].strip(' ')
    except:
        state = "No state"
    address = city + ', ' + state
    try:
        zipcode =  page_soup.find(itemprop="postalCode").contents[0].strip(' ')#page_soup.find(class_="postal-code").contents[0]
    except:
        zipcode = "No zipcode"
    try:
        phone = page_soup.find(class_='tel').contents[0].strip('\n')
    except:
        phone = "No phone number"

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
    if state_url in cache_diction.keys():
        print("Using Cache")
        stateurl_data = cache_diction[state_url]
    else:
        print("Fetching")
        cache_diction[state_url] = requests.get(state_url).text
        stateurl_data = cache_diction[state_url]
        cache_data(CACHEFILE, state_url, cache_diction, stateurl_data)
    
    national_site_inst_list = []
    state_soup = BeautifulSoup(stateurl_data, 'html.parser')
    all_site_link = state_soup.find_all(class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left')
    for link in all_site_link:
        park_link = link.find('a')['href']
        site_url = BASEURL + '/' + park_link + '/' + 'index.htm'
        national_site_inst_list.append(get_site_instance(site_url))

    # print(national_site_inst_list)
    return national_site_inst_list

# get_sites_for_state('https://www.nps.gov/state/mi/index.htm')

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
    baseurl_api = 'http://www.mapquestapi.com/search/v2/radius?'
    API_KEY = secrets.API_KEY
    params = {'key': API_KEY, 'origin': site_object.zipcode, 'radius': 10, 'maxMatches': 10, "ambiguities": "ignore", "outFormat": "json"}#start here
    param_strings = []
    connector = '&'
    for k in params.keys():
        param_strings.append(f'{k}={params[k]}')
    param_strings.sort()
    unique_key = baseurl_api + connector.join(param_strings)
    # print(unique_key)
    # return unique_key
    if unique_key in cache_diction.keys():
        print("Using Cache")
        response_j = cache_diction[unique_key]
    else:
        print("Fetching")
        response = requests.get(unique_key)
        response_j = response.json()
        cache_diction[unique_key] = response_j
        unique_key_data = cache_diction[unique_key]
        cache_data(CACHEFILE, unique_key, cache_diction, unique_key_data)
    
   
    i = 0
    while i < int(response_j['resultsCount']) and i<10:#i < len(response_j['hostedData']) and
        if len(response_j['searchResults'][i]['name'])>0:
            name = response_j['searchResults'][i]['name']
        else:
            name = "no name"
        if len(response_j['searchResults'][i]['fields']['group_sic_code_name'])>0:
            category = response_j['searchResults'][i]['fields']['group_sic_code_name']
        else:
            category = "no category"
        if len(response_j['searchResults'][i]['fields']['address'])>0:
            address = response_j['searchResults'][i]['fields']['address']
        else:
            address = "no address"
        if len(response_j['searchResults'][i]['fields']['city'])>0:
            city_name = response_j['searchResults'][i]['fields']['city']
        else:
            city_name = "no city"
        print(f'- {name} ({category}): {address}, {city_name}')
        i += 1
    return response_j


if __name__ == "__main__":
    while True:
        state_url_dict = build_state_url_dict()
        input_var = input('Enter a state name (case-insensitive) or "exit": ')
        if input_var.lower() == "exit":
            print()
            print("Bye!")
            break
        elif input_var.lower() not in state_url_dict.keys():
            print("[Error] Enter proper state name")
        elif input_var.lower() in state_url_dict.keys():
            state_url_user = state_url_dict[input_var.lower()]
            inst_list_func = get_sites_for_state(state_url_user)
            print("---------------------------------------")
            print(f'List of national sites in {input_var}')
            print("---------------------------------------")
            for z in range(len(inst_list_func)):
                print("[" + str(z+1) + "]" + " " + inst_list_func[z].info())
            while True:
                input_num = input("Enter a number for places nearby to site, or 'back' to select a new state, or 'exit': ")
                if input_num.lower() == "back":
                    break
                elif input_num.isnumeric() == True and int(input_num) > len(inst_list_func):
                    print("Please enter a number within your search results.")
                    continue
                elif input_num.isnumeric() == True and (int(input_num)-1) < len(inst_list_func):
                    print("---------------------------------------")
                    print(f'Places near {(inst_list_func[int(input_num)-1]).name}')
                    print("---------------------------------------")
                    get_nearby_places(inst_list_func[int(input_num)-1])
                elif input_num.lower() == "exit":
                    print()
                    print('Bye!')
                    exit()
            



