import requests
import pandas as pd
import json


class DocStoreRequestBuilder():
    """
    Class for creating DOCStore requests
    """

    def __init__(self):
        self.url = "https://tyrion.scibite.com:9999"
        self.input_file_path = ''
        self.payload = {"output": "json"}
        self.options = {}
        self.binary_content = None
        self.basic_auth = ()
        self.verify_request = True

    def set_basic_auth(self, username='', password='', verification=True):
        """
        Pass basic authentication credentials
        **ONLY change verification if you are calling a known source**
        :param username: username to be used for basic authentication
        :param password: password to be used for basic authentication
        :param verification: if set to False requests will ignore verifying the SSL certificate, can also pass the path
        to a certificate file
        """
        self.basic_auth = (username, password)
        self.verify_request = verification

    def set_url(self, url):
        """
        Set the URL of the DOCStore instance e.g. for local instance http://localhost:9090/termite
        :param url: the URL of the DOCStore instance to be hit
        """
        self.url = url

    def get_dcc_docs(self, entity_list, source, options_dict):
        """
        Retrieve document co-occurrence of provided entities
        :param entity_list: list of entities to be searched for
        :param source: name of data source(s) to be searched against
        :param options_dict: search parameters
        :return: results of search in json format
        """
        base_url = self.url
        query_url = (base_url) + "/api/ds/v1/search/co/document/{}/*/*/*".format(source)
        entity_string = " ".join(entity_list)

        options = {"fmt": "json",
                   "fields": "*",
                   "terms": entity_string,
                   "limit": "10",
                   "from": "0",
                   "facettype": "NONE",
                   "significantTerms": "false",
                   "excludehits": "false",
                   "sortby": "document_date:desc",
                   }

        try:
            for k, v in options_dict.items():
                if k in options.keys():
                    options[k] = v
        except:
            pass

        response = requests.get(query_url, params=options, verify=False)  # More possible authentication
        resp_json = response.json()

        return resp_json

    def get_dcc_docs_query(self, query_string, source, options_dict):
        """
        Retrieve document co-occurrence of provided entities
        :param query_string: query to be completed
        :param source: name of data source(s) to be searched against
        :param options_dict: search parameters
        :return: results of search in json format
        """
        base_url = self.url
        query_url = (base_url) + "/api/ds/v1/search/document/{}/*/*/*".format(source)

        options = {"fmt": "json",
                   "fields": "*",
                   "query": query_string,
                   "limit": "10",
                   "from": "0",
                   "facettype": "NONE",
                   "significantTerms": "false",
                   "excludehits": "false",
                   "sortby": "document_date:desc",
                   "filters": ""
                   }

        try:
            for k, v in options_dict.items():
                if k in options.keys():
                    options[k] = v
        except:
            pass

        response = requests.get(query_url, params=options, verify=False)  # More possible authentication
        resp_json = response.json()

        return resp_json

    def get_scc_docs(self, entity_list, source, options_dict):
        """
        Retrieve sentence co-occurrence of provided entities
        :param entity_list: list of entities to be searched for
        :param source: name of data source(s) to be searched against
        :param options_dict: search parameters
        :return: results of search in json format
        """
        base_url = self.url
        query_url = (base_url) + "/api/ds/v1/search/co/sentence/sentencedetail/flat/{}/*/*/*".format(
            source)
        entity_string = " ".join(entity_list)

        options = {"fmt": "json",
                   "fields": "*",
                   "terms": entity_string,
                   "inorder": "false",
                   "slop": "2",
                   "limit": "10",
                   "from": "0",
                   "sortby": "document_date:desc",
                   "zip": "false"}

        try:
            for k, v in options_dict.items():
                if k in options.keys():
                    options[k] = v
        except:
            pass

        response = requests.get(query_url, params=options, verify=False)  # May need to add authentication details here
        resp_json = response.json()

        return resp_json


def get_docstore_dcc_df(json):
    """
    Converts document co-occurrence json into a dataframe
    :param json: dcc json
    :return: dcc dataframe
    """
    all_hits = json["hits"]
    all_hit_list = []

    for hit in all_hits:
        hit_dict = {}

        doc_title = ""
        doc_text = ""
        for section in (hit["section"]):
            if section["sectionId"] == 0:
                doc_title += section["titleText"]
                doc_text += section["text"]
        doc_id = hit["id"]
        authors = hit["authors"]
        doc_date = (hit["documentDate"])[0:10]

        hit_dict.update([("document_id", doc_id), ("title", doc_title), ("authors", authors),
                         ("date", doc_date), ("text", doc_text)])
        all_hit_list.append(hit_dict)

    dcc_df = pd.DataFrame(all_hit_list)
    return (dcc_df)


def get_docstore_scc_df(json):
    """
     Converts sentence co-occurrence json into a dataframe
     :param json: scc json
     :return: scc dataframe
     """
    all_hits = json["hits"]
    all_hits_list = []

    for hit in all_hits:
        hit_dict = {}
        doc_id = hit["docId"]
        doc_date = (hit["docDate"])[0:10]
        doc_sent = hit["sentence"]

        hit_dict.update([("document_id", doc_id), ("document_date", doc_date), ("scc_sentence", doc_sent)])
        all_hits_list.append(hit_dict)

    scc_df = pd.DataFrame(all_hits_list, columns=["document_id", "document_date", "scc_sentence"])
    return (scc_df)


sample_query = "( type:ANAT AND id:PROTYP$PROTYP9 ) NOT ( id:GENE$ALK OR id:GENE$RET OR id:GENE$PDL-1 OR id:GENE$PARP OR id:GENE$BRAF OR id:GENE$EGFR OR id:GENE$mTOR OR id:GENE$CDK4 OR id:GENE$BDK )"
dic_opt = {
    "filters": json.dumps({"rangefilters": [{"field": "document_date", "from": "2003-10-31", "to": "2019-10-31"}]})}

sample_query_2 = "type:ANAT"
docs = DocStoreRequestBuilder()
print(docs.get_dcc_docs_query(
    sample_query_2,
    "immunonc", dic_opt))
