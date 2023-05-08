import requests
import os
import json

token = os.getenv('NOTION_TOKEN')
database_id = os.getenv('NOTION_DATABASE_ID')
headers = {
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
    "Authorization": f"Bearer {token}"
}


url = f"https://api.notion.com/v1/databases/{database_id}/query"
json_data = {
    # 絞り込み(データベースだけに絞るなど)
    "filter": {
        "property": "Index",
        "relation": {
            "contains": "9a62bea55ee147a09549ddd716b5ebbf"
        },
    },
    # ソート順
    "sorts": [
        {
            "direction": "descending",
            "timestamp": "last_edited_time"
        }
    ]
}
response = requests.post(url, json=json_data, headers=headers)

property = response.json()['results'][0]['properties']
property.pop('Created time')
property.pop('Last edited time')
id = response.json()['results'][0]['id']

print("1. ", property)


def fetch_block(id):
    url = f"https://api.notion.com/v1/blocks/{id}/children"
    response = requests.get(url, headers=headers)

    children = []
    for i in response.json()['results']:
        if i['type'] == 'column_list' or i['type'] == 'column':
            children.append(
                {
                    "object": "block",
                    "has_children": i['has_children'],
                    "type": i['type'],
                    i['type']: {
                        "children": fetch_block(i['id'])
                    },
                })
        else:
            children.append(
                {
                    "object": "block",
                    "has_children": i['has_children'],
                    "type": i['type'],
                    i['type']: i[i['type']],
                })
    return children


children = fetch_block(id)
print("2. ", children)

url = "https://api.notion.com/v1/pages"
payload = {
    "parent": {
        "database_id": database_id
    },
    "properties": property,
    "children": children
}
print("3. ", payload)

response = requests.post(url, json=payload, headers=headers)
print("4. ", response.text)
