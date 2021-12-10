import biothings.hub.dataload.uploader
import os

import biothings
import config
import requests
biothings.config_for_app(config)

MAP_URL = "https://raw.githubusercontent.com/SuLab/outbreak.info-resources/master/outbreak_resources_es_mapping_v3.json"
MAP_VARS = ["evaluations"]

# when code is exported, import becomes relative
try:
    from covid_figshare.parser import load_annotations as parser_func
except ImportError:
    from .parser import load_annotations as parser_func


class FigshareUploader(biothings.hub.dataload.uploader.BaseSourceUploader):

    main_source = "covid_altmetrics"
    name = "covid_altmetrics"
    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.altmetric.com/products/altmetric-api/',
            'url': 'https://www.altmetric.com/'
        }
    }
    idconverter = None
    storage_class = biothings.hub.dataload.storage.BasicStorage

    def load_data(self, data_folder):
        if data_folder:
            self.logger.info("Load data from directory: '%s'", data_folder)
        return parser_func()

    @classmethod
    def get_mapping(klass):
        r = requests.get(MAP_URL)
        if(r.status_code == 200):
            mapping = r.json()
            mapping_dict = { key: mapping[key] for key in MAP_VARS }
            return mapping_dict
