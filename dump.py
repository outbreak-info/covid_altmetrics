import os

import biothings, config
biothings.config_for_app(config)
from config import DATA_ARCHIVE_ROOT

import biothings.hub.dataload.dumper
import datetime

class AltmetricsDumper(biothings.hub.dataload.dumper.DummyDumper):
    # type: resource
    SRC_NAME = "covid_altmetrics"
    # override in subclass accordingly
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.altmetric.com/products/altmetric-api/',
            'url': 'https://www.altmetric.com/'
        }
    }

    SCHEDULE = "0 0 * * 0"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_release()

    def set_release(self):
        self.release = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M')
