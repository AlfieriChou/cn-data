import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
from matplotlib import font_manager

from mysql import connection

font_manager.fontManager.addfont('font/SimHei.ttf')
matplotlib.rc('font', family='SimHei')
china = gpd.read_file('geo/china_v1.json')
area_code_list = [
  110000,
  120000,
  130000,
  140000,
  150000,
  210000,
  220000,
  230000,
  310000,
  320000,
  330000,
  340000,
  350000,
  360000,
  370000,
  410000,
  420000,
  430000,
  440000,
  450000,
  460000,
  500000,
  510000,
  520000,
  530000,
  540000,
  610000,
  620000,
  630000,
  640000,
  650000,
  710000,
  810000,
  820000,
]
provinces = area_code_list
dates = []


def get_area_data_list():
  with connection.cursor() as cursor:
    cursor.execute(
      """
      select year, area, area_code, rate from birthrate where year < 2023 order by year      
      """
    )
    data_list = cursor.fetchall()
    dict_list = []
    for row in data_list:
      if row['year'] not in dates:
        dates.append(row['year'])
      dict_list.append(
        {
          'name': row['area'],
          'group': row['area'],
          'date': row['year'],
          'value': row['count'],
        }
      )

    return dict_list


base_list = get_area_data_list()

dict_list = []


def search(name, date, dict_list):
  return [
    element
    for element in dict_list
    if element['name'] == name and element['date'] == date
  ]


for date in dates:
  for area in area_list:
    t = search(area, date, base_list)
    if len(t) == 0:
      dict_list.append(
        {
          'name': area,
          'group': area,
          'date': date,
          'value': 0,
        }
      )
    else:
      dict_list.append(t[0])

df0 = pd.DataFrame.from_dict(dict_list)
connection.close()

china_w_needed_provinces = china[china.adcode.isin(provinces)]

df = pd.DataFrame(
  {
    'date': df0['date'].tolist(),
    'province': df0['name'].tolist(),
    'value': df0['value'].tolist(),
  }
)

fig, ax = plt.subplots(figsize=(16, 9))
fontsize = 8

# 左下角添加的排名列表
ax_rank = fig.add_axes([0.05, 0.05, 0.4, 0.3])  # 位置和大小可以调整

ims = []
dates = df['date'].unique()
vmin, vmax = df['value'].min(), df['value'].max()


def update_fig(i):
  ax.clear()  # 清空当前帧
  ax_rank.clear()  # 清空排名表

  # 绘制地理数据
  geos = china_w_needed_provinces['geometry']
  value = df[df['date'] == dates[i]]['value'].tolist()
  artist = gpd.plotting._plot_polygon_collection(ax, geos, value, cmap='Reds')

  # 更新地图上的省份名称和其他信息
  for lon, lat, province in zip(
    china_w_needed_provinces.lon,
    china_w_needed_provinces.lat,
    china_w_needed_provinces.name,
  ):
    ax.text(lon, lat, province, fontsize=fontsize)

  ax.set_title(f'{dates[0]}至{dates[-1]}各省出生率数据 {dates[i]}')
  ax.set_axis_off()

  # 添加颜色条
  fig = ax.get_figure()
  cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
  sm = plt.cm.ScalarMappable(
    cmap='Reds', norm=plt.Normalize(vmin=vmin, vmax=vmax)
  )
  sm._A = []
  fig.colorbar(sm, cax=cax)

  # 排名列表
  current_df = df[df['date'] == dates[i]]
  sorted_df = current_df.sort_values(by='value', ascending=False).head(
    6
  )  # 取前6名

  # 设置排名显示的样式
  ax_rank.set_title('省份出生率数量前6名', fontsize=fontsize)
  ax_rank.barh(sorted_df['province'], sorted_df['value'], color='red')
  ax_rank.invert_yaxis()  # 排名从上到下排列
  ax_rank.set_xlabel('出生率次数', fontsize=fontsize)

  ims.append(artist)
  return ims


anim = FuncAnimation(
  fig,
  update_fig,
  interval=1000,
  repeat_delay=500,
  frames=len(df['date'].unique()),
)

# 保存动画
anim.save(
  filename='video/birthrate_with_top6_ranking.mp4', writer='ffmpeg'
)
