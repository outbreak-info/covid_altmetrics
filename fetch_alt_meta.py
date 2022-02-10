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



def fetch_altmetrics_meta(script_path,test=False):
    RESULTSPATH = os.path.join(script_path,'results/')
    result_data_file = os.path.join(RESULTSPATH,'altmetric_annotations.json')
    print('fetching altmetrics: ',datetime.now())
    if test == True:
        cleanidlist = ["NCT03348670", "NCT00173459", "NCT00571389", "pmid32835433", "pmid32835716", "10.1101/2020.01.19.911669", "10.1101/2020.01.21.914929", "10.5281/zenodo.5776439", "29489394"]
        testidlist = random.sample(cleanidlist, 5)
        print(testidlist)
        altdump = generate_dump(script_path,testidlist)
    else:
        with open(os.path.join(RESULTSPATH,'cleanids.pickle'),'rb') as savefile:
            cleanidlist = pickle.load(savefile)
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
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)

adapter = TimeoutHTTPAdapter(timeout=2.5,max_retries=retry_strategy)
httprequests.mount("https://", adapter)
httprequests.mount("http://", adapter)

script_path = pathlib.Path(__file__).parent.absolute()
fetch_altmetrics_meta(script_path)