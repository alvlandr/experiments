# encoding: utf-8

"""
Copy existing dashboard.

In case you need to copy existing dashboard for some reason (e.g. you want to
see the same visualization from different queries/data sources) you can use
the script.
Workflow is the following:
- Read src dashboard (defined by DASHBOARD_SLUG)
- Create new empty dashboard (target) with the same name concatenated with
  'AUTOMATICALLY CREATED'
- Go through the widgets of source dashboard, check if they were created by
  copying (property _text_ contains 'AC'), if not then copy the query and
  visualization
"""

import requests


API_KEY = ''
BASE_URL = ''
DASHBOARD_SLUG = ''

DASHBOARD_CREATE_URL = BASE_URL + f'dashboards?api_key={API_KEY}'
WIDGET_CREATE_URL = BASE_URL + f'widgets?api_key={API_KEY}'
QUERY_CREATE_URL = BASE_URL + f'queries?api_key={API_KEY}'
VIS_CREATE_URL = BASE_URL + f'visualizations?api_key={API_KEY}'

DASHBOARD_GET_URL = BASE_URL + 'dashboards/' + DASHBOARD_SLUG + f'?api_key={API_KEY}'
QUERY_MOD_URL = BASE_URL + 'queries/' + '{qid}' + f'?api_key={API_KEY}'

# Get source dashboard
src_dashboard = requests.get(DASHBOARD_GET_URL)
src_dashboard_json = src_dashboard.json()

# Create new empty dashboard
target_dashboard_name = 'AUTOMATICALLY CREATED ' + src_dashboard_json['name']
target_dashboard = requests.post(
    DASHBOARD_CREATE_URL,
    json={"name": target_dashboard_name})
target_dashboard_json = target_dashboard.json()

# Go through all its visualizations and queries - copying them
widget_needed_keys = ['dashboard_id', 'text', 'width', 'options']
for i, widget in enumerate(src_dashboard_json['widgets']):
    src_visualization = widget['visualization']

    src_query = src_visualization['query']
    if widget['text'].find('AC') == -1:
        src_query['name'] = 'AUTOMATICALLY CREATED ' + src_query['name']
        src_query_cutted = {
            'query': src_query['query'],
            'name': src_query['name'],
            'data_source_id': src_query['data_source_id'],
            'is_draft': False,
            'options': src_query['options']
        }
        target_query = requests.post(QUERY_CREATE_URL, json=src_query_cutted)
        target_query_json = target_query.json()
        q_url = QUERY_MOD_URL.format(qid=target_query_json['id'])
        target_query_activated = requests.post(q_url, json={'is_draft': False})

        target_visualization_json = dict()
        target_visualization_json['query'] = target_query_activated.json()
        target_visualization_json['options'] = src_visualization['options']
        target_visualization_json['type'] = src_visualization['type']
        target_visualization_json['name'] = src_visualization['name']
        target_visualization_json['query_id'] = target_query_activated.json()['id']
        target_visualization = requests.post(
            VIS_CREATE_URL,
            json=target_visualization_json,
        )
        target_visualization_id = target_visualization.json()['id']

    else:
        target_visualization_id = src_visualization['id']

    # Prepare and insert widget
    widget['dashboard_id'] = target_dashboard_json['id']
    cur_widget = dict()
    for k in widget_needed_keys:
        cur_widget[k] = widget[k]
    cur_widget['visualization_id'] = target_visualization_id
    cur_widget['text'] = 'AC'

    post_result = requests.post(WIDGET_CREATE_URL, json=cur_widget)
