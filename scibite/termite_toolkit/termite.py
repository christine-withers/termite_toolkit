"""

  ____       _ ____  _ _         _____ _____ ____  __  __ _ _         _____           _ _    _ _
 / ___|  ___(_) __ )(_) |_ ___  |_   _| ____|  _ \|  \/  (_) |_ ___  |_   _|__   ___ | | | _(_) |_
 \___ \ / __| |  _ \| | __/ _ \   | | |  _| | |_) | |\/| | | __/ _ \   | |/ _ \ / _ \| | |/ / | __|
  ___) | (__| | |_) | | ||  __/   | | | |___|  _ <| |  | | | ||  __/   | | (_) | (_) | |   <| | |_
 |____/ \___|_|____/|_|\__\___|   |_| |_____|_| \_\_|  |_|_|\__\___|   |_|\___/ \___/|_|_|\_\_|\__|


TERMiteRequestBuilder- make requests to the TERMite API and process results.

"""

__author__ = 'SciBite DataScience'
__version__ = '2.0'
__copyright__ = '(c) 2019, SciBite Ltd'
__license__ = 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License'

import requests
import os
import pandas as pd


class TermiteRequestBuilder():
    """
    Class for creating TERMite requests.
    """

    def __init__(self):
        self.url = 'http://localhost:9090/termite'
        self.input_file_path = ''
        self.payload = {"output": "json"}
        self.options = {}
        self.binary_content = None
        self.basic_auth = ()
        self.verify_request = True

    def set_basic_auth(self, username='', password='', verification=True):
        """
        Pass basic authentication credentials.
        **ONLY change verification if you are calling a known source**

        :param username: username to be used for basic authentication
        :param password: password to be used for basic authentication
        :param verification: if set to False requests will ifnore verifying the SSL certificate, can also pass the path to a certfile
        :return:
        """
        self.basic_auth = (username, password)
        self.verify_request = verification

    def set_url(self, url):
        """
        Set the URL of the TERMite instance e.g. for local instance http://localhost:9090/termite

        :param url: the URL of the TERMite instance to be hit
        :return:
        """
        self.url = url

    def set_binary_content(self, input_file_path):
        """
        For annotating file content, send file path string and process file as a binary
        multiple files of the same type can be scanned at once if placed in a zip archive.

        :param input_file_path: file path to the file to be sent to TERMite
        :return:
        """
        file_obj = open(input_file_path, 'rb')
        file_name = os.path.basename(input_file_path)
        self.binary_content = {"binary": (file_name, file_obj)}

    def set_text(self, string):
        """
        Use this for tagging raw text e.g. if looping through some file content

        :param string: text to be sent to TERMite
        :return:
        """
        self.payload["text"] = string

    def set_options(self, options_dict):
        """
        For bulk setting multiple TERMite API options in a single call, send a dictionary object here

        :param options_dict: a dictionary of options to be passed to TERMite
        :return:
        """

        if 'output' in options_dict:
            self.payload['output'] = options_dict['output']

        options = []
        for k, v in options_dict.items():
            options.append(k + "=" + str(v))
        option_string = '&'.join(options)
        if "opts" in self.payload:
            self.payload["opts"] = option_string + "&" + self.payload["opts"]
        else:
            self.payload["opts"] = option_string

    #######
    # individual options for applying the major TERMite settings
    #######

    def set_fuzzy(self, bool):
        """
        Use fuzzy matching?

        :param bool: set to True if fuzzy matching is to be enabled
        :return:
        """
        input = bool_to_string(bool)
        if "opts" in self.payload:
            self.payload["opts"] = "fzy.promote=" + input + "&" + self.payload["opts"]
        else:
            self.payload["opts"] = "fzy.promote=" + input
        self.payload["fuzzy"] = input

    def set_subsume(self, bool):
        """
        Take longest hit where an entity is a hit against more than one dictionary
        :param bool: set subsume if True
        :return:
        """
        input = bool_to_string(bool)
        self.payload["subsume"] = input

    def set_entities(self, string):
        """
        Limit the entities to be annotated

        :param string: a comma separated string of entity types, e.g. 'DRUG,GENE'
        :return:
        """
        self.payload["entities"] = string

    def set_input_format(self, string):
        """
        Set input format e.g. txt, medline.xml, node.xml, pdf, xlsx

        :param string: string input format
        :return:
        """
        self.payload["format"] = string

    def set_output_format(self, string):
        """
        Set output format e.g. tsv, json, doc.json

        :param string: provide the output format to be used
        :return:
        """
        self.payload["output"] = string

    def set_reject_ambiguous(self, bool):
        """
        Automatically reject any hits flagged as ambiguous.

        :param bool: set True to reject any ambiguous hits
        :return:
        """
        input = bool_to_string(bool)
        if "opts" in self.payload:
            self.payload["opts"] = self.payload["opts"] + "&rejectAmbig=" + input
        else:
            self.payload["opts"] = "rejectAmbig=" + input

    def set_max_docs(self, integer):
        """
        When tagging a zip file of multiple documents, limit how many to scan
        also applies where there are multiple document records in a single xml e.g. from a medline XML export

        :param integer: number of documents to limit annotation too
        :return:
        """
        self.payload["maxDocs"] = integer

    def set_no_empty(self, bool):
        """
        Reject all documents where there were no hits

        :param bool: if True do not return any docs with no hits
        :return:
        """
        input = bool_to_string(bool)
        self.payload["noEmpty"] = input

    def execute(self, display_request=False):
        """
        Once all settings are done, POST the parameters to the TERMite RESTful API

        :param display_request: if True request will be printed out before being submitted
        :return:
        """
        if display_request:
            print("REQUEST: ", self.url, self.payload)
        try:
            if self.binary_content and bool(self.basic_auth):
                response = requests.post(self.url, data=self.payload, files=self.binary_content, auth=self.basic_auth,
                                         verify=self.verify_request)
            elif self.binary_content and bool(self.basic_auth) == False:
                response = requests.post(self.url, data=self.payload, files=self.binary_content)
            elif not self.binary_content and bool(self.basic_auth):
                response = requests.post(self.url, data=self.payload, verify=self.verify_request, auth=self.basic_auth)
            else:
                response = requests.post(self.url, data=self.payload)
        except Exception as e:
            return print(
                "Failed with the following error {}\n\nPlease check that TERMite can be accessed via the following URL {}\nAnd that the necessary credentials have been provided (done so using the set_basic_auth() function)".format(
                    e, self.url))

        if "json" in self.payload["output"]:
            return response.json()
        else:
            return response.text


def bool_to_string(bool):
    """
    Convert a boolean to a string

    :param bool: provide boolean to be converted
    :return:
    """
    string = str(bool)
    string = string.lower()

    return string


def annotate_files(url, input_file_path, options_dict):
    """
    Wrapper function to execute a TExpress request for annotating individual files or a zip archive

    :param url: url of TERMite instance
    :param input_file_path: path to file to be annotated
    :param options_dict: dictionary of options to be used during annotation
    :return:
    """
    t = TermiteRequestBuilder()
    t.set_url(url)
    t.set_binary_content(input_file_path)
    t.set_options(options_dict)
    result = t.execute()

    return result


def annotate_text(url, text, options_dict):
    """
    Wrapper function to execute a TExpress request for annotating strings of text

    :param url: url of TERMite instance
    :param input_file_path: path to file to be annotated
    :param options_dict: dictionary of options to be used during annotation
    :return:
    """
    t = TermiteRequestBuilder()
    t.set_url(url)
    t.set_text(text)
    t.set_options(options_dict)
    result = t.execute()

    return result


def get_entity(termite_home, entity_id, entity_type):
    """
    Entity lookup function, given and entity type (e.g. GENE, INDICATION) and entity ID (e.g. CSF1, D010024)
    creates and runs GET call of the format: http://localhost:9090/termite/toolkit/tool.api?t=describe&id=INDICATION:D001249
    returns TERMite json

    :param termite_home: url to TERMite instance
    :param entity_id: id of entity of interest
    :param entity_type: type of entity of interest
    :return:
    """
    url = ("%s/toolkit/tool.api?t=describe&id=%s:%s" % (termite_home, entity_type, entity_id))
    response = requests.get(url)

    if response.ok:
        entity_json = response.json()
        return entity_json

    else:
        return response.status_code


def get_entity_details(termite_home, entity_id, entity_type):
    """
    Returns a subset of metadata from the get_entity result: ID, name, mappings to external IDs

    :param termite_home: url to TERMite instance
    :param entity_id: id of entity of interest
    :param entity_type: type of entity of interest
    :return:
    """
    details = {"id": entity_id, "type": entity_type, "name": "", "mappings": []}
    entity_meta = get_entity(termite_home, entity_id, entity_type)
    if len(entity_meta["TOOL_RESULT"]) > 0:
        e = entity_meta["TOOL_RESULT"][0]
        details["name"] = e["name"]
        if "mappings" in e:
            mappings = e["mappings"]
            for m in mappings:
                items = m.split('|')
                details["mappings"].append(items)

    return details


def process_payload(filtered_hits, response_payload, filter_entity_types, doc_id='', reject_ambig=True, score_cutoff=0,
                    remove_subsumed=True):
    """
    Parses the termite json output to filter out only entity types of interest and their major metadata
    includes rules for rejecting ambiguous or low-relevance hits.

    :param filtered_hits:
    :param response_payload:
    :param filter_entity_types:
    :param doc_id:
    :param reject_ambig:
    :param score_cutoff:
    :param remove_subsumed:
    :return:
    """
    for entity_type, entity_hits in response_payload.items():
        if entity_type in filter_entity_types:
            for entity_hit in entity_hits:
                nonambigsyns = entity_hit["nonambigsyns"]
                entity_score = entity_hit["score"]
                if reject_ambig == True:
                    if nonambigsyns == 0:
                        continue
                if "subsume" in entity_hit and remove_subsumed == True:
                    if True in entity_hit["subsume"]:
                        continue
                if entity_hit["score"] >= score_cutoff:
                    hit_id = entity_hit["hitID"]
                    entity_id = entity_type + '$' + hit_id
                    entity_name = entity_hit["name"]
                    hit_count = entity_hit["hitCount"]
                    if entity_id in filtered_hits:
                        filtered_hits[entity_id]["hit_count"] += hit_count
                        filtered_hits[entity_id]["doc_count"] += 1
                        filtered_hits[entity_id]["doc_id"].append(doc_id)
                        if entity_score > filtered_hits[entity_id]["max_relevance_score"]:
                            filtered_hits[entity_id]["max_relevance_score"] = entity_score
                    else:
                        filtered_hits[entity_id] = {"id": hit_id, "type": entity_type, "name": entity_name,
                                                    "hit_count": hit_count, "max_relevance_score": entity_score,
                                                    "doc_id": [doc_id], "doc_count": 1}

    return filtered_hits


def get_entity_hits_from_json(termite_json_response, filter_entity_types, reject_ambig=True, score_cutoff=0):
    """


    :param termite_json_response: JSON returned from TERMite
    :param filter_entity_types: string of entity types separated by commas
    :param reject_ambig: boolean
    :param score_cutoff: a numeric value between 1-5
    :return:
    """
    filtered_hits = {}
    filter_entity_types = filter_entity_types.replace(' ', '').split(',')
    if "RESP_MULTIDOC_PAYLOAD" in termite_json_response:
        doc_results = termite_json_response["RESP_MULTIDOC_PAYLOAD"]
        for doc_id, response_payload in doc_results.items():
            filtered_hits = process_payload(filtered_hits, response_payload, filter_entity_types,
                                            reject_ambig=reject_ambig, score_cutoff=score_cutoff, doc_id=doc_id)

    elif "RESP_PAYLOAD" in termite_json_response:
        response_payload = termite_json_response["RESP_PAYLOAD"]
        filtered_hits = process_payload(filtered_hits, response_payload, filter_entity_types, reject_ambig=reject_ambig,
                                        score_cutoff=score_cutoff)

    return filtered_hits


def docjsonx_payload_records(docjsonx_response_payload, reject_ambig=True, score_cutoff=0, remove_subsumed=True):
    """
    Parses TERMite doc.JSONx payload into records, includes rules to filter out ambiguous and low-relevance hits.

    :param docjsonx_response_payload: doc.JSONx TERMite response.
    :param reject_ambig: boolean
    :param score_cutoff: a numerical value between 1-5
    :param remove_subsumed: boolean
    :return: TERMite response in records format
    """
    payload = []
    for doc in docjsonx_response_payload:
        if 'termiteTags' in doc.keys():
            for entity_hit in doc['termiteTags']:
                # update document record with entity hit record
                entity_hit.update(doc)
                del entity_hit['termiteTags']

                # filtering
                if reject_ambig is True and entity_hit['nonambigsyns'] == 0:
                    continue
                if "subsume" in entity_hit and remove_subsumed is True:
                    if True in entity_hit['subsume']:
                        continue
                if entity_hit['score'] >= score_cutoff:
                    payload.append(entity_hit)

    return (payload)


def json_payload_records(response_payload, reject_ambig=True, score_cutoff=0, remove_subsumed=True):
    """
    Parses TERMite json payload into records, includes rules to filter out ambiguous and low-relevance hits.

    :param response_payload: REP_PAYLOAD of JSON TERMite response
    :param reject_ambig: boolean
    :param score_cutoff: a numerical value between 1-5
    :param remove_subsumed: boolean
    :return: TERMite response in records format
    """
    payload = []
    for entity_type, entity_hits in response_payload.items():
        for entity_hit in entity_hits:
            # filtering
            if reject_ambig is True and entity_hit['nonambigsyns'] == 0:
                continue
            if "subsume" in entity_hit and remove_subsumed is True:
                if True in entity_hit['subsume']:
                    continue
            if entity_hit['score'] >= score_cutoff:
                payload.append(entity_hit)

    return (payload)


def payload_records(termiteResponse, reject_ambig=True, score_cutoff=0, remove_subsumed=True):
    """
    Parses TERMite JSON or doc.JSONx output into records format.

    :param termiteResponse: JSON or doc.JSONx TERMite response
    :param reject_ambig: boolean
    :param score_cutoff: a numerical value between 1-5
    :param remove_subsumed: boolean
    :return: TERMite response in records format
    """
    payload = []

    if "RESP_MULTIDOC_PAYLOAD" in termiteResponse:
        for docID, termite_hits in termiteResponse['RESP_MULTIDOC_PAYLOAD'].items():
            payload = payload + json_payload_records(termite_hits, reject_ambig=reject_ambig,
                                                     score_cutoff=score_cutoff, remove_subsumed=remove_subsumed)
    elif "RESP_PAYLOAD" in termiteResponse:
        payload = payload + json_payload_records(termiteResponse['RESP_PAYLOAD'], reject_ambig=reject_ambig,
                                                 score_cutoff=score_cutoff, remove_subsumed=remove_subsumed)
    else:
        payload = docjsonx_payload_records(termiteResponse, reject_ambig=reject_ambig,
                                           score_cutoff=score_cutoff, remove_subsumed=remove_subsumed)

    return (payload)


def get_termite_dataframe(termiteResponse, cols_to_add="", reject_ambig=True, score_cutoff=0,
                          remove_subsumed=True):
    """
    Parses TERMite JSON or doc.JSONx into a dataframe of hits, filtering out ambiguous and low-relevance hits.
    By default returns docID, entityType, hitID, name, score, realSynList, totnosyns, nonambigsyns, frag_vector_array.
    Additional hit information not included in the default output can be included by use of a comma separated list.

    :param termiteResponse: JSON or doc.JSONx response from TERMite
    :param cols_to_add: comma separated list of additional fields to include
    :param reject_ambig: boolean
    :param score_cutoff: a numerical value between 1-5
    :param remove_subsumed: boolean
    :return: dataframe of TERMite hits
    """

    payload = payload_records(termiteResponse, reject_ambig=reject_ambig,
                              score_cutoff=score_cutoff, remove_subsumed=remove_subsumed)
    df = pd.DataFrame(payload)

    cols = ["docID", "entityType", "hitID", "name", "score", "realSynList", "totnosyns", "nonambigsyns",
            "frag_vector_array"]

    if cols_to_add:
        cols_to_add = cols_to_add.replace(" ", "").split(",")
        try:
            cols = cols + cols_to_add
            return (df[cols])
        except KeyError as e:
            print("Invalid column selection.", e)
    else:
        return (df[cols])


def get_entity_hits_from_docjsonx(termiteResponse, filter_entity_types):
    """
    Parses doc.JSONx TERMite response and returns a summary of the hits.

    :param termiteResponse: doc.JSONx TERMite response
    :param filter_entity_types: comma separated list
    :return:
    """
    processed = docjsonx_payload_records(termiteResponse)

    filtered_hits = {}
    for entity_hit in processed:
        # pprint(entity_hit)
        hit_id = entity_hit['hitID']
        entityType = entity_hit['entityType']
        entity_id = entityType + '$' + hit_id
        entity_name = entity_hit['name']
        hit_count = entity_hit['hitCount']
        entity_score = entity_hit['score']
        doc_id = entity_hit['docID']

        if entityType in filter_entity_types:
            if entity_id in filtered_hits:
                filtered_hits[entity_id]['hit_count'] += hit_count
                if entity_score > filtered_hits[entity_id]['max_relevance_score']:
                    filtered_hits[entity_id]['max_relevance_score'] = entity_score
                if doc_id not in filtered_hits[entity_id]['doc_id']:
                    filtered_hits[entity_id]['doc_id'].append(doc_id)
                    filtered_hits[entity_id]['doc_count'] += 1
            else:
                filtered_hits[entity_id] = {"id": hit_id, "type": entityType, "name": entity_name,
                                            "hit_count": hit_count,
                                            "max_relevance_score": entity_score, "doc_id": [doc_id], "doc_count": 1}

    return (filtered_hits)


def all_entities(termiteResponse):
    """
    Parses TERMite response and returns a list of VOCab modules with hits.

    :param termiteResponse: JSON or doc.JSONx TERMite response
    :return: list
    """
    payload = payload_records(termiteResponse)

    entities_used = []
    for entity_hit in payload:
        if entity_hit['entityType'] not in entities_used:
            entities_used.append(entity_hit['entityType'])

    return (entities_used)


def all_entities_df(termiteResponse):
    """
    Parses JSON or doc.JSONx TERMite response into summary of hits dataframe

    :param termiteResponse: JSON or doc.JSONx TERMite response
    :return: pandas dataframe
    """

    # identify all entitiy hit types in the text
    entities_used = all_entities(termiteResponse)
    entities_string = (',').join(entities_used)

    if "RESP_MULTIDOC_PAYLOAD" in termiteResponse or "RESP_PAYLOAD" in termiteResponse:
        filtered_hits = get_entity_hits_from_json(termiteResponse, entities_string)
    else:
        filtered_hits = get_entity_hits_from_docjsonx(termiteResponse, entities_string)

    df = pd.DataFrame(filtered_hits).T

    return (df)


def entity_freq(termiteResponse):
    """
    Parses TERMite JSON or doc.JSONx response and returns dataframe of entity type frequencies.

    :param termiteResponse: JSON or doc.JSONx TERMite response
    :return: pandas dataframe
    """

    df = get_termite_dataframe(termiteResponse)

    values = pd.value_counts(df['type'])
    values = pd.DataFrame(values)
    return (values)


def top_hits_df(termiteResponse, selection=10, entitySubset=None, includeDocs=False):
    """
    Parses JSON or doc.JSONx TERMite response and returns a pandas dataframe of the most frequent hits. By default the
    top 10 most frequent hits are returned. The entity types to include can be set by a comma separated list.
    For multidoc results the documents in which hits occur can be included.

    :param termiteResponse: JSON or doc.JSONx TERMite response
    :param selection: number of most frequent hits to return
    :param entitySubset: comma separated list
    :param includeDocs: boolean
    :return: pandas dataframe
    """

    # get entity hits and sort by hit_count
    df = get_termite_dataframe(termiteResponse)
    df.sort_values(by=['hit_count'], ascending=False, inplace=True)
    df2 = df.copy()

    # select relevant columns and filtering
    if includeDocs is True:
        columns = [3, 5, 6, 2, 1]
    else:
        columns = [3, 5, 6, 2]
    if entitySubset is not None:
        entitySubset = entitySubset.replace(" ", "").split(",")
        criteria = df2['type'].isin(entitySubset)
        return (df2[criteria].iloc[0:selection, columns])
    else:
        return (df2.iloc[0:selection, columns])
