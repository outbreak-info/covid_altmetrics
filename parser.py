import os
import json
import requests
import random
from datetime import datetime
import time
import pathlib

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 5 # seconds

class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


query_types = {"pubs":'((_exists_:pmid)or(_exists__:doi))',
               "clins":'(curatedBy.name:"ClinicalTrials.gov")'}


def fetch_src_size(query_type):
    pubmeta = httprequests.get("https://api.outbreak.info/resources/query?q="+query_type)
    pubjson = json.loads(pubmeta.text)
    pubcount = int(pubjson["total"])
    return(pubcount)


#### Pull ids from a json file use dois whenever possible
def get_ids_from_json(jsonfile):
    idlist = []
    for eachhit in jsonfile["hits"]:
        try:
            doi = eachhit["doi"]
            if doi!= "":
                idlist.append(doi)
        except:
            if eachhit["_id"] not in idlist:
                idlist.append(eachhit["_id"])
    return(idlist)


#### Ping the API and get the ids and dois and scroll through until they're all obtained
def get_source_ids(query_type):
    source_size = fetch_src_size(query_type)
    r = httprequests.get("https://api.outbreak.info/resources/query?q="+query_type+"&fields=_id,doi&fetch_all=true")
    response = json.loads(r.text)
    idlist = get_ids_from_json(response)
    try:
        scroll_id = response["_scroll_id"]
        while len(idlist) < source_size:
            r2 = httprequests.get("https://api.outbreak.info/resources/query?q="+query_type+"&fields=_id,doi&fetch_all=true&scroll_id="+scroll_id)
            response2 = json.loads(r2.text)
            idlist2 = set(get_ids_from_json(response2))
            tmpset = set(idlist)
            idlist = tmpset.union(idlist2)
            try:
                scroll_id = response2["_scroll_id"]
            except:
                print("no new scroll id")
            time.sleep(1)
        return(idlist)
    except:
        return(idlist)

    
def map_to_main_id(eachid):
    try:
        r = httprequests.get('https://api.outbreak.info/resources/query?q=doi:"'+eachid+'"')
        response = json.loads(r.text)
        outbreak_id = response['hits'][0]['_id']
    except:
        outbreak_id = eachid
    return(outbreak_id)


def generate_curator():
    todate = datetime.now()
    curatedByObject = {"@type": "Organization", "identifier": "altmetric",  
                       "name": "Altmetric", "affiliation": ["Digital Science"],
                       "curationDate": todate.strftime("%Y-%m-%d")}
    return(curatedByObject)


def clean_ids(idlist):
    pmidlist = [ x for x in idlist if "pmid" in x ]
    doilist = [ x for x in idlist if "10." in x ] 
    nctlist = [ x for x in idlist if "NCT" in x ]
    cleanidlist = list(set(pmidlist).union(set(doilist).union(set(nctlist))))
    #missinglist = [ x for x in idlist if x not in cleanidlist ] ##(only for checking incompatible ids)
    return(cleanidlist)
    
    
def load_key(script_path):
    cred_path = os.path.join(script_path, 'credentials.json')
    with open(cred_path) as f:
        credentials = json.load(f) 
        apikey = credentials["key"]
    return(apikey)


def fetch_meta(key_url,pubid):
    base_url = 'https://api.altmetric.com/v1/'
    if 'pmid' in pubid:
        api_call = base_url+'pmid/'+pubid.replace("pmid","")+key_url
    elif 'NCT' in pubid:
        api_call = base_url+'nct_id/'+pubid+key_url       
    else:
        api_call = base_url+'doi/'+pubid+key_url
    r = httprequests.get(api_call)
    try:
        hourlylimit = r.headers["X-HourlyRateLimit-Limit"]
        secondslimit = int(hourlylimit)/3600
        sleeptime = 1/secondslimit
    except:
        sleeptime = 1
    if r.status_code==200:
        rawmeta = json.loads(r.text)
        error=False
    else:
        rawmeta={}
        error=True
    return(rawmeta,error,sleeptime)
    
    
def generate_dump(script_path,cleanidlist):
    apikey = load_key(script_path)
    key_url = '?key='+apikey
    altdump = []
    for eachid in cleanidlist:
        aspectslist = ['cited_by_fbwalls_count','cited_by_feeds_count','cited_by_gplus_count',
                       'cited_by_msm_count','cited_by_posts_count','cited_by_rdts_count',
                       'cited_by_tweeters_count','cited_by_videos_count','cited_by_accounts_count',
                       'readers_count']
        readerlist = ['citeulike','mendeley','connotea']
        rawmeta,error,sleeptime = fetch_meta(key_url,eachid)
        if error == False :
            authorObject = generate_curator()
            altdict = {"@type":"AggregateRating", "author":authorObject, "identifier":rawmeta["altmetric_id"],
                       "url":rawmeta["details_url"], "image":rawmeta["images"]["small"], "name":"Altmetric",
                       "reviewAspect":"Altmetric score", "ratingValue":rawmeta["score"]}
            reviewlist = []
            for eachrating in aspectslist:
                a_review = {"@type":"Review","reviewAspect":eachrating}
                try:
                    a_review["reviewRating"]={"ratingValue":rawmeta[eachrating]}
                except:
                    a_review["reviewRating"]={"ratingValue":0}
                reviewlist.append(a_review)
            for eachreader in readerlist:
                a_review = {"@type":"Review","reviewAspect":eachreader+" reader count"}
                try:
                    a_review["reviewRating"]={"ratingValue":rawmeta["readers"][eachreader]}
                except:
                    a_review["reviewRating"]={"ratingValue":0}
                reviewlist.append(a_review)
            altdict["reviews"]=reviewlist
            outbreak_id = map_to_main_id(eachid)
            dumpdict = {"_id":outbreak_id, 
                       "evaluations":[altdict]}
            altdump.append(dumpdict)
        time.sleep(sleeptime)
    return(altdump)


def get_altmetrics_update(script_path,test=False):
    RESULTSPATH = os.path.join(script_path,'results/')
    result_data_file = os.path.join(RESULTSPATH,'altmetric_annotations.json')
    print('fetching ids: ',datetime.now())
    if test == True:
        pubidlist = ["pmid32835433","pmid32835716","2020.01.19.911669","2020.01.21.914929","zenodo.3976542"]
        clinidlist = ["NCT03348670","NCT00173459","NCT00571389"]
    else:
        pubidlist = get_source_ids(query_types["pubs"])
        clinidlist = get_source_ids(query_types["clins"])
    idlist = list(set(pubidlist).union(set(clinidlist)))
    print('cleaning up ids: ',datetime.now())
    cleanidlist = clean_ids(idlist)
    print('fetching altmetrics: ',datetime.now())
    if test == True:
        testidlist = random.sample(cleanidlist, 5)
        altdump = generate_dump(script_path,testidlist)
    else:
        altdump = generate_dump(script_path,cleanidlist)
    print('exporting results: ',datetime.now())
    with open(result_data_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(altdump, indent=4))
        
        
#### MAIN ####
httprequests = requests.Session()

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)

adapter = TimeoutHTTPAdapter(timeout=2.5,max_retries=retry_strategy)
httprequests.mount("https://", adapter)
httprequests.mount("http://", adapter)

script_path = pathlib.Path(__file__).parent.absolute()
get_altmetrics_update(script_path)