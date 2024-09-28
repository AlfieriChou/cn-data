import requests
import json

url = 'https://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=fsnd&rowcode=reg&colcode=sj&wds=%5B%7B%22wdcode%22%3A%22zb%22,%22valuecode%22%3A%22A030201%22%7D%5D&dfwds=%5B%5D&k1=1727503141929'

def get_data_list ():
  headers = {
    'User-Agent': 'insomnia/10.0.0'
  }
  r = requests.get(url, headers=headers)
  return json.loads(r.text)

ret = get_data_list()

if ret['returncode'] == 200:
  data_list = ret['returndata']['datanodes']
  wd_data_list = ret['returndata']['wdnodes']
  area_data = next(item for item in wd_data_list if item['wdname'] == '地区')
  area_data_list = area_data['nodes']
  print(len(area_data_list), len(data_list))
