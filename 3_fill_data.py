import json
import math
from pprint import pprint
import subprocess
import time

#and this scrip aims at parsing more detailed info of the followers we got before
start = time.time()
with open('followers.json', 'r') as f:
    followers = json.load(f)

command_template = """curl 'https://www.instagram.com/{username}/?__a=1' -H 'authority: www.instagram.com' -H 'accept: */*' -H 'sec-fetch-dest: empty' -H 'x-ig-www-claim: hmac.AR3NtmCkHqA09LnmbxYr161pWu2li1DCx3hGu8b3HApqEbDG' -H 'x-requested-with: XMLHttpRequest' -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36' -H 'x-ig-app-id: 936619743392459' -H 'sec-fetch-site: same-origin' -H 'sec-fetch-mode: cors' -H 'referer: https://www.instagram.com/{your_user_name}/' -H 'accept-language: en-US,en;q=0.9,ru;q=0.8' -H 'cookie: ig_cb=1; ig_did=BF059198-B2B3-4211-BA6C-B32605F5716C; mid=XkKJIQAEAAHsEXa7rddiMYgjVoVq; fbm_124024574287414=base_domain=.instagram.com; fbsr_124024574287414=L0pFE9-X_PfCK7itY95Mp6iElSe_BZFtwwWlV3LL6g0.eyJ1c2VyX2lkIjoiMTAwMDAxOTI5Mjc3MDQ0IiwiY29kZSI6IkFRQjJMbnI3YURFY2NpWk9vcFlaOGhIbVlvcmdYX2oycGF6V3RpZ1prdHR6emVaRGhGeTJzd3lQNXktZl9rcHJYbHQ0am1rMDY3Vkd1RGVNWUQ1My01azJrMFd0OHhITlQ1aHlGZkY0ZXhEeW4zd19XWEo2YXlRV0J4aWtqRHc1STRGZXdmdjVWdnNZdzFaV1oxcmc5UzZPUjhJUE1MdnBnOFR5alVUdGdCazRxdjk1YzlBZ0Y0OERwemZpSjk2dFNyNVF2M1hMYXRsU0VIUVJMOGhmdkNsa0pYZ3VKR0JpSnNnWXJPdUgxeVRRX3dvOXBaUHNSRmJVdzAwWVY5MUE0WlBaWi1ZcWo5QUkxTnhsai00QlVreldfTGVOelJoNkd4WVhlaENIVFpMYW94WVR4SjNEYVJnZHo5WE5QdjY1cU9McGdfUlZKNS1TRVFGRG5KV0Q3TEVsIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUY0aHVwNVI0YXRaQkl3dERxQldnTFhvb0JsOU1kTUlCcDBaQmtuMlpDWkJKYlV5SWRpWkNRYm45RHFIODhtS1pDR0VaQnRsVmx4UGdlZTQ0QUZWRUlCMkZWVUE2UVhsSU1zbHU5cVpDd1hwVXBGTGsyNlkzcGVMV3pXMFdVMk1uQkFWN2RiM244WkN3RTFhbkhtQzcxbENUWkF5WWVmNjZaQzZFNm40V2VtWE5uMyIsImFsZ29yaXRobSI6IkhNQUMtU0hBMjU2IiwiaXNzdWVkX2F0IjoxNTg1NDk3NjI4fQ; csrftoken=VvBrWsIvMzG9KrGamVtyFXVNwQKDvaQZ; shbid=7289; shbts=1585497629.0177615; ds_user_id=your_user_id; sessionid=your_user_id%3Ah6u1HsUr2SjvSi%3A1; rur=ATN; urlgen="{{\"31.134.191.149\": 42668\054 \"85.10.230.13\": 24940\054 \"62.112.8.212\": 49981}}:1jIdDT:v32AApuqhb379PJd4K1qGepVPBs"' --compressed > temp.json"""

index = 0
followers_filled = []
for user in followers:
    subprocess.run(command_template.format(username=user['username']), shell=True, capture_output=True)
    with open('temp.json', 'r') as f:
        try:
            data = json.load(f)
        except:
            print(f'There is an issue in JSON parsing for {user["username"]}')
            continue
    
    if 'graphql' not in data:
        time.sleep(5)
        print(f'THere is no graphql in server response, we got: {data}')
        continue
    photos_edges = data['graphql']['user']['edge_owner_to_timeline_media']
    last_photos_posted_in_one_day = False
    if photos_edges and len(photos_edges['edges']) > 2:
        last_photos_posted_at = [photos_edges['edges'][i]['node']['taken_at_timestamp'] for i in range(3)]
        difference = int(math.fabs(min(last_photos_posted_at) - max(last_photos_posted_at)))
        if difference < 86400:
            last_photos_posted_in_one_day = True

    user['follows'] = data['graphql']['user']['edge_follow']['count']
    user['posts'] = data['graphql']['user']['edge_owner_to_timeline_media']['count']
    user['biography'] = data['graphql']['user']['biography']
    user['last_photos_posted_in_one_day'] = last_photos_posted_in_one_day
    followers_filled.append(user)

    print(f'{index}/{len(followers)} Iteration')
    time.sleep(0.5 if index % 10 != 0 else 3)
    if index % 10 == 0:
        with open(f'filled/followers_filled_{index}.json', 'w') as f:
            json.dump(followers_filled, f)
    index += 1

with open('followers_filled.csv', 'w') as f:
    f.write(f"Name;Username;Follows;Posts;Bio;Last picture in 1 day \n")
    for user in followers_filled:
        full_name = user["full_name"].replace('"', "")
        bio = user["biography"].replace('"', "")
        f.write(f'"{full_name}";{user["username"]};{user["follows"]};{user["posts"]};"{bio}";'
                f'{1 if user["last_photos_posted_in_one_day"] else 0}\n')

end = time.time()
print(end - start)

print((end - start)//60, 'mins and ', round((end - start)%60,1), 'secs')
