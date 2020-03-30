import glob
import json
from pprint import pprint


#we'll parse the files we've created in 1_get_followers.py and write all the data in a separate document
files = glob.glob("json/*.json")
followers = {}
for file in files:
    with open(file, 'r') as f:
        data = json.load(f)
        for user in data['data']['user']['edge_followed_by']['edges']:
            user_info = user['node']
            followers[user_info['username']] = {
                'id': user_info['id'],
                'username': user_info['username'],
                'followed_by_viewer': user_info['followed_by_viewer'],
                'full_name': user_info['full_name']
            }
pprint(followers)

with open('followers.json', 'w') as f:
    json.dump(list(followers.values()), f)

