import requests
import os
from bs4 import BeautifulSoup
import json

DIR = os.getcwd()
FOLDER = DIR+'\\archive'
LEGACY_VOLS = {'23', '24', '25', '26', '27', '28', '29', '36', '39', '40', '41', '42', '43', '50'}

def parse_json(file):
    with open(file, 'r') as f:
        content = f.read()
    return json.loads(content)


def write_json(data, file):
    with open(file, 'w') as f:
        json.dump(data, f)
    f.close()


def get_archive():
    '''
    Takes:
        none
    Returns:
        none

    uses get_urls() to retrieve, saves them using write_pdf()
    '''
    urls = parse_json('urls_scrapped.json')
    volumes_complete = parse_json('volumes_complete.json')

    for vol, issues in urls.items():
        if vol in volumes_complete:
            continue

        vol_folder = FOLDER+'\\vol_'+vol
        if not os.path.exists(vol_folder):
            os.mkdir(vol_folder)

        print('Downloading volume '+vol)
        for iss, links in issues.items():
            iss_file = vol_folder+'\\issue_'+iss+'.pdf'
            if not os.path.exists(iss_file):
                for link in links:
                    response = requests.get(link)
                    with open(iss_file, 'wb') as f:
                        f.write(response.content)
                f.close()

        if vol != len(urls):
            volumes_complete[vol] = True
            write_json(volumes_complete, 'volumes_complete.json')


def get_urls():
    '''
    Takes:
        none
    Returns:
        dict "urls": keys are volume number, value is a set of all issue urls in that volume

    retrives all urls from both websites
    '''
    def get_legacy(vol):
        '''
        Takes:
            vol: type int, the volume being scrapped
        Returns:
            none

        gets legacy archives from legacy site and adds to "urls" dict in scope
        '''
        url_start = 'http://tech.mit.edu/archives/VOL_0'+vol+'/'
        response = requests.get(url_start)
        soup = BeautifulSoup(response.text, 'html.parser')
        num = 1

        for link in soup.select("a[href$='.pdf']"):
            link = str(link)
            url_end = link.split('"')[1] #relative link to issue pdf
            if vol not in {'22', '35', '38', '49'}: #some non-legacy archives come up; exclude them
                if vol in urls:
                    if str(num) in urls[vol]:
                        urls[vol][str(num)].append(url_start+url_end)
                    else:
                        urls[vol][str(num)] = [url_start+url_end]
                else:
                    urls[vol] = {str(num): [url_start+url_end]}
                num += 1
        write_json(urls, 'urls_scrapped.json')


    print('Retrieving urls from thetech.com...')
    urls = parse_json('urls_scrapped.json')
    url_start = 'https://thetech.com/issues'
    response = requests.get(url_start)
    soup = BeautifulSoup(response.text, 'html.parser')

    for link in soup.find_all(class_='issue'):
        link = str(link)
        url_end = link.split('"')[3].replace('/issues', '') #get string in volume/issue format
        vol, iss = url_end.split('/')[1:] #get string issue
        if vol not in urls:
            write_json(urls, 'urls_scrapped.json')
            print("Now retrieving urls from volume", vol)
            urls[vol] = {}

        if len(urls[vol]) < int(iss):
            #get link to actual pdf
            response = requests.get(url_start+url_end+'/pdf')
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf = str(soup.find("iframe")).split('"')[1]
            #add to dict
            if pdf == '/pdfs/original/missing.png': #if there is no pdf
                response = requests.get(url_start+url_end)
                soup = BeautifulSoup(response.text, 'html.parser')
                try:
                    li = str(soup.find_all(class_="headline")).split('"')
                    articles = [li[i] for i in range(3, len(soup), 4)]
                except:
                    print('No archive of volume', str(vol), 'issue', iss, 'found.')
            else:
                urls[vol][iss] = [pdf]

    print('Retrieving legacy urls...')
    for vol in LEGACY_VOLS:
        get_legacy(vol)


if __name__ == '__main__':
    #if archive folder does not exist, make it
    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)

    if not os.path.exists(DIR+'\\urls_scrapped.json'):
        with open('urls_scrapped.json', 'w') as outfile:
            json.dump({}, outfile)

    if not os.path.exists(DIR+'\\volumes_complete.json'):
        with open('volumes_complete.json', 'w') as outfile:
            json.dump({}, outfile)

    get_urls()
    get_archive()
