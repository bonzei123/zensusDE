from functions.base_headers import base_headers
import requests.auth


def get_userdata(access_token):
    headers = base_headers()
    headers.update({"Authorization": "bearer " + access_token})
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    me_json = response.json()
    ret = {'name': me_json['name'], 'created': me_json['created'], 'userid': me_json['id']}
    return ret
