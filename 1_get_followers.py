import json
from pprint import pprint
import subprocess
import time
import urllib.parse

#Using developers tools we'll need to get the cURL that opens one's followers.

#We'll track the time that was required to perform the script
start = time.time()

url_base = 'https://www.instagram.com/graphql/query/?'
#we'll generate several lists of users, the index will numerate them
index = 1

#the variable indicates scrolled pages, it is necessary for the very first iteration,
#as it parses the first page of followers withour scrolling them
after = None 

#>json/followers_{index}.json indicates the document which will be used to save gathered data
command_template = """curl '{url}' -H 'authority: www.instagram.com' -H 'x-ig-www-claim: hmac.AR3NtmCkHqA09LnmbxYr161pWu2li1DCx3hGu8b3HApqEbDG' -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36' -H 'accept: */*' -H 'sec-fetch-dest: empty' -H 'x-requested-with: XMLHttpRequest' -H 'x-csrftoken: VvBrWsIvMzG9KrGamVtyFXVNwQKDvaQZ' -H 'x-ig-app-id: 936619743392459' -H 'sec-fetch-site: same-origin' -H 'sec-fetch-mode: cors' -H 'referer: https://www.instagram.com/your_username/' -H 'accept-language: en-US,en;q=0.9,ru;q=0.8' -H 'cookie: ig_cb=1; ig_did=BF059198-B2B3-4211-BA6C-B32605F5716C; mid=XkKJIQAEAAHsEXa7rddiMYgjVoVq; fbm_124024574287414=base_domain=.instagram.com; fbsr_124024574287414=L0pFE9-X_PfCK7itY95Mp6iElSe_BZFtwwWlV3LL6g0.eyJ1c2VyX2lkIjoiMTAwMDAxOTI5Mjc3MDQ0IiwiY29kZSI6IkFRQjJMbnI3YURFY2NpWk9vcFlaOGhIbVlvcmdYX2oycGF6V3RpZ1prdHR6emVaRGhGeTJzd3lQNXktZl9rcHJYbHQ0am1rMDY3Vkd1RGVNWUQ1My01azJrMFd0OHhITlQ1aHlGZkY0ZXhEeW4zd19XWEo2YXlRV0J4aWtqRHc1STRGZXdmdjVWdnNZdzFaV1oxcmc5UzZPUjhJUE1MdnBnOFR5alVUdGdCazRxdjk1YzlBZ0Y0OERwemZpSjk2dFNyNVF2M1hMYXRsU0VIUVJMOGhmdkNsa0pYZ3VKR0JpSnNnWXJPdUgxeVRRX3dvOXBaUHNSRmJVdzAwWVY5MUE0WlBaWi1ZcWo5QUkxTnhsai00QlVreldfTGVOelJoNkd4WVhlaENIVFpMYW94WVR4SjNEYVJnZHo5WE5QdjY1cU9McGdfUlZKNS1TRVFGRG5KV0Q3TEVsIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUY0aHVwNVI0YXRaQkl3dERxQldnTFhvb0JsOU1kTUlCcDBaQmtuMlpDWkJKYlV5SWRpWkNRYm45RHFIODhtS1pDR0VaQnRsVmx4UGdlZTQ0QUZWRUlCMkZWVUE2UVhsSU1zbHU5cVpDd1hwVXBGTGsyNlkzcGVMV3pXMFdVMk1uQkFWN2RiM244WkN3RTFhbkhtQzcxbENUWkF5WWVmNjZaQzZFNm40V2VtWE5uMyIsImFsZ29yaXRobSI6IkhNQUMtU0hBMjU2IiwiaXNzdWVkX2F0IjoxNTg1NDk3NjI4fQ; csrftoken=VvBrWsIvMzG9KrGamVtyFXVNwQKDvaQZ; shbid=7289; shbts=1585497629.0177615; ds_user_id=your_user id; sessionid=260253524%3Ah6u1HsUr2SjvSi%3A1; rur=ATN; urlgen="{{\"31.134.191.149\": 42668\054 \"85.10.230.13\": 24940\054 \"62.112.8.212\": 49981}}:1jIacF:HYkjicLoo2wBhgtzVWy09I-IHZo"' --compressed > json/followers_{index}.json"""

followers_in_progress = 0
#we'll have several iterations and urls will differ, thus, the url will be generated inside the cicle
while True:
    
    #after_value is empty for the first iteration as there is no scrollowing
    after_value = f',"after":"{after}"' if after else ''
    variables = f'{{"id":"260253524","first":30{after_value}}}'
    
    get_params = {
        'query_hash': 'c76146de99bb02f6415203be841dd25a',
        'variables': variables
        }
    
    ws_url = url_base + urllib.parse.urlencode(get_params)
    
    result = subprocess.run(command_template.format(url = ws_url, index = index), shell = True, capture_output = True)
    
    #an additional check to make sure the request was executed correctly
    if result.returncode != 0:
        exit('Failed request')
       
    with open(f'json/followers_{index}.json', 'r') as f:
        data = json.load(f)
    
    #this conditions is meant to check whether there is another page to scroll
    #to make sure we do not get in an infinite loop
    if not data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
        break
    
    #here we collect the data and count how many requests are processed
    after = data['data']['user']['edge_followed_by']['page_info']['end_cursor']
    all_followers = data['data']['user']['edge_followed_by']['count']
    in_current_batch = len(data['data']['user']['edge_followed_by']['edges'])
    followers_in_progress += in_current_batch
    print(f'{followers_in_progress}/{all_followers} processed')

    #an additional delay in request to avoid potential blocks from the Instagram side
    time.sleep(5 if index % 10 != 0 else 20)
    
    index +=1
#the documents were written, let's see how much time te process took     
end = time.time()
print((end - start)//60, 'mins and ', round((end - start)//60, 1), 'secs')

