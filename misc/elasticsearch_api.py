# encoding: utf-8

"""
Single function to retrieve ES logs with scrolling.
"""

import json

from elasticsearch import Elasticsearch


def get_logs(config) -> list:
    """
    Retrieve logs from ElasticSearch.

    :param config: either dict with config or filepath to config file
        Configuration file fields:
        url: ElasticSearch host
        e_index: ElasticSearch index (part of data path)
        body: Body of the request
        conn_dur: ElasticSearch scroll time -  duration when connection
        will not be lost (for large responses)
        chunck_size: response size for ElasticSearch
    :return: list with logs chunks
    """

    if type(config) is str:
        with open('config_timeouts.json') as cfile:
            config = json.load(cfile)
    elif type(config) is dict:
        pass
    else:
        raise TypeError('Input data type should be either dict or str (filepath to conf)')

    url = config['url']
    e_index = config['e_index']
    conn_dur = config['conn_dur']
    chunck_size = config['chunck_size']
    body = json.dumps(config['body'])

    es = Elasticsearch(url)
    full_response = []
    response = es.search(
        index=e_index,
        body=body,
        scroll=conn_dur,
        size=chunck_size,
    )
    full_response.append(response)
    while response['hits']['hits']:
        response = es.scroll(
            scroll=conn_dur,
            scroll_id=response['_scroll_id'],
        )
        full_response.append(response)

    return full_response


if __name__ == '__main__':
    URL_DEFAULT = '%URL_PLACEHOLDER'
    INDEX_DEFAULT = '%ID_PLACEHOLDER'
    CONNECTION_DUR = '2m'
    RESPONSE_SIZE = 2000
    DATA_DEFAULT = {
      "query": {
        "bool": {
          "must": [
            {
              "term": {
                "container.name": "detector-taxi-ride"
              }
            },
            {
              "range": {
                "@timestamp": {
                  "gte": "2020-07-15T00:00:00",
                  "lte": "now-1h"
                }
              }
            }
          ]
        }
      },
      "_source": "smth.*"
    }

    config_demo = {
        'url': URL_DEFAULT,
        'e_index': INDEX_DEFAULT,
        'conn_dur': CONNECTION_DUR,
        'chunck_size': RESPONSE_SIZE,
        'body': DATA_DEFAULT,
    }

    result = get_logs(config_demo)

    print('Chuncks number:', len(result))
