import requests
import json

from mysql import connection

url = 'https://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=fsnd&rowcode=reg&colcode=sj&wds=%5B%7B%22wdcode%22%3A%22zb%22,%22valuecode%22%3A%22A030201%22%7D%5D&dfwds=%5B%5D&k1=1727503141929'


def get_data_list():
  headers = {'User-Agent': 'insomnia/10.0.0'}
  r = requests.get(url, headers=headers)
  return json.loads(r.text)


def write_birthrate_list_to_db(data_list, connection):
  try:
    with connection.cursor() as cursor:
      # 创建表（如果尚未存在）
      cursor.execute("""
      CREATE TABLE IF NOT EXISTS birthrate (
        id VARCHAR(64) PRIMARY KEY,
        year INT NOT NULL,
        area_code VARCHAR(32) NOT NULL,
        area VARCHAR(32) NOT NULL,
        rate FLOAT NOT NULL,
        INDEX idx_id (id),
        INDEX idx_year (year),
        INDEX idx_area_code (area_code),
        INDEX idx_area (area),
        INDEX idx_rate (rate)
      )
      """)

      # 插入数据
      # 构建INSERT语句
      insert_query = """
        INSERT IGNORE INTO birthrate (
          id,
          rate,
          year,
          area_code,
          area
        ) VALUES (
          %s, %s, %s, %s, %s
        )
      """

      # 构建并执行多个插入语句
      for row in data_list:
        print(row)
        # 执行INSERT语句
        cursor.execute(insert_query, row)

      connection.commit()

  finally:
    print('write birthrate list done')


ret = get_data_list()

if ret['returncode'] == 200:
  data_list = ret['returndata']['datanodes']
  wd_data_list = ret['returndata']['wdnodes']
  area_data = next(item for item in wd_data_list if item['wdname'] == '地区')
  area_data_list = area_data['nodes']
  print(len(area_data_list), len(data_list))
  birthrate_list = []
  for item in data_list:
    rate = item['data']['data']
    year = int(item['wds'][2]['valuecode'])
    area_code = item['wds'][1]['valuecode']
    area_info = next(
      item for item in area_data_list if item['code'] == area_code
    )
    area = area_info['name']
    birthrate_list.append(
      [
        str(year) + '_' + area_code,
        rate,
        year,
        area_code,
        area,
      ]
    )
  print(birthrate_list)
  write_birthrate_list_to_db(birthrate_list, connection)
  connection.close()
