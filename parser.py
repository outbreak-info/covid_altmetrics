import json
import requests
from datetime import datetime

### Get the size of the source (to make it easy to figure out when to stop scrolling)
def fetch_src_size():
    pubmeta = requests.get("https://api.outbreak.info/resources/resource/query?q=@type:Publication")
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

def get_source_ids():
    source_size = fetch_src_size()
    r = requests.get("https://api.outbreak.info/resources/resource/query?q=@type:Publication&fields=_id,doi&fetch_all=true")
    response = json.loads(r.text)
    idlist = get_ids_from_json(response)
    try:
        scroll_id = response["_scroll_id"]
        while len(idlist) < source_size:
            r2 = requests.get("https://api.outbreak.info/resources/resource/query?q=@type:Publication&fields=_id,doi&fetch_all=true&scroll_id="+scroll_id)
            response2 = json.loads(r2.text)
            idlist2 = set(get_ids_from_json(response2))
            tmpset = set(idlist)
            idlist = tmpset.union(idlist2)
            try:
                scroll_id = response2["_scroll_id"]
            except:
                print("no new scroll id")
        return(idlist)
    except:
        return(idlist)

def generate_curator():
    todate = datetime.now()
    curatedByObject = {"@type": "Organization", "identifier": "altmetric",  
                              "name": "Altmetric", "affiliation": "Digital Science", 
                              "curationDate": todate.strftime("%Y-%m-%d")}
    return(curatedByObject)

def clean_ids(idlist):
    pmidlist = [ x for x in idlist if "pmid" in x ]
    doilist = [ x for x in idlist if "10." in x ] 
    cleanidlist = list(set(pmidlist).union(set(doilist)))
    missinglist = [ x for x in idlist if x not in cleanidlist ] 
    return(cleanidlist)

def load_key():
    #cred_path = os.path.join(DATA_PATH, 'credentials.json')
    cred_path = 'credentials.json'
    with open(cred_path) as f:
        credentials = json.load(f) 
        apikey = credentials["key"]
    return(apikey)

def fetch_meta(pubid):
    apikey = load_key()
    base_url = 'https://api.altmetric.com/v1/'
    key_url = '?key='+apikey
    if 'pmid' in pubid:
        api_call = base_url+'pmid/'+pubid.replace("pmid","")+key_url
    else:
        api_call = base_url+'doi/'+pubid+key_url
    r = requests.get(api_call)
    if r.status_code==200:
        rawmeta = json.loads(r.text)
        error=False
    else:
        rawmeta={}
        error=True
    return(rawmeta,error)


