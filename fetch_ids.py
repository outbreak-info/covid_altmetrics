import os
import json
import requests
import random
from datetime import datetime
import time
import pathlib
import pickle
from common import *

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 5 # seconds
    
    
def get_ids_for_altmetrics(script_path,test=False):
    RESULTSPATH = os.path.join(script_path,'results/')
    result_data_file = os.path.join(RESULTSPATH,'altmetric_annotations.json')
    try:
        print('fetching ids: ',datetime.now())
        query_types = {"pubs":'((_exists_:pmid)or(_exists_:doi))',
                       "clins":'(curatedBy.name:"ClinicalTrials.gov")'}
        if test == True:
            pubidlist = ["pmid32835433","pmid32835716","10.1101/2020.01.19.911669","10.1101/2020.01.21.914929","10.5281/zenodo.5776439","29489394"]
            clinidlist = ["NCT03348670","NCT00173459","NCT00571389"]
        else:
            pubidlist = get_source_ids(query_types["pubs"])
            clinidlist = get_source_ids(query_types["clins"])
        idlist = list(set(pubidlist).union(set(clinidlist)))
        print('cleaning up ids: ',datetime.now())
        cleanidlist = clean_ids(idlist)
        with open(os.path.join(RESULTSPATH,'cleanids.pickle'),'wb') as savefile:
            pickle.dump(cleanidlist,savefile)
    except:
        with open(os.path.join(RESULTSPATH,'cleanids.pickle'),'rb') as savefile:
            cleanidlist = pickle.load(savefile)

        
        
#### MAIN ####
httprequests = requests.Session()

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)

adapter = TimeoutHTTPAdapter(timeout=2.5,max_retries=retry_strategy)
httprequests.mount("https://", adapter)
httprequests.mount("http://", adapter)

script_path = pathlib.Path(__file__).parent.absolute()
get_ids_for_altmetrics(script_path)