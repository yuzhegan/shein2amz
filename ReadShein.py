# encoding='utf-8

# @Time: 2021-12-29
# @File: %
#!/usr/bin/env
from icecream import ic
import pandas as pd
import xlsxwriter

# %%
# 文件编码格式需要处理下
SheinData = pd.read_csv("reslut.csv", encoding = "utf-8")

# %%
splist = []
for index, row in SheinData.iterrows():
    if "-" not in str(row["sku"]) : #没有-的就是父sku
        splist.append(index)

# %%
def get_ilocindex(splist):
    new_split = []
    for i in range(len(splist)-1):
        new_split.append([splist[i],splist[i+1]])
    return new_split

# 将数据[0,4,8]拆分成两个两个index, [[0,4], [4,8]]分别为一个lisitng, 用到.iloc截取
# ilocindex = get_ilocindex(splist)
# ic(ilocindex)

# %%
# splist 的index每两个之间就是一条listing 
# df = SheinData.iloc[0:4]
# ic(df)
def get_sheinspdata(SheinData, splist):
    spdata = []
    ilocindex = get_ilocindex(splist)
    for item in ilocindex:
        sheindata = SheinData[item[0]:item[1]]
        sheindata = sheindata.reset_index(drop=True)
        spdata.append(sheindata)
    return spdata
# %%
# 将每条listing放入列表
sheinspdata = get_sheinspdata(SheinData, splist)
# ic(sheinspdata[0])
## ---------------------以上把shein的数据做了处理,拆分成多个dataframe----

# %%
# 这里需要处理模板数据,将模板数据和shein数据进行重组
template_data = pd.read_excel("template-jp.xlsm", header=2, sheet_name="テンプレート")
bullet_header= pd.read_excel("template-jp.xlsm", sheet_name="テンプレート")
headers = bullet_header.iloc[0:2]
# headers 表头有空的列,Unnamed: 5 , 有Unnamed的的列名替换成空
new_columns =[]
for column in headers.columns:
    if "Unnamed" in column:
        column = ""
    new_columns.append(column)
headers.columns = new_columns
# ic(template_data)
# %%
# 创建新的模板用来新建数据
new_datas = pd.DataFrame(columns=template_data.columns) #用来存放单个listing的数据



shein_data = sheinspdata[0] #测试一条数据
# TODO: 循环的方式,分父产品子产品做出每个lisitng  <29-12-21, yuzhe> #
# 将Sheindata 中的bullet_point 转成字典格式
dict_bullet = eval(shein_data.iloc[0]['bullet_point'])
# ic(dict_bullet)
for index, row in shein_data.iterrows():
    if index == 0: # parent sku
        # Series >> DataFrame to_frame方法, 还有就是转字典, 再转list
        new_data = template_data.iloc[0].to_frame()
        new_data = pd.DataFrame(new_data.values.T, columns= new_data.index)
        # ic(new_data.columns)
    else: # child sku
        # TODO: Something  <29-12-21, yuzhe> #
        new_data = template_data.iloc[1].to_frame()
        new_data = pd.DataFrame(new_data.values.T, columns= new_data.index)
        new_data["size_name"] = row['size_name']
        new_data["size_map"] = row['size_name']
        new_data["color_name"] = row['color']
        new_data["color_map"] = row['color']
        # 30%的毛利 取两位小数
        # price = str(row["price"])
        price = str(row["price"]).replace(",", "").strip("¥")
        if str(price) != "" and str(price) != None:
            new_data["standard_price"] = round(float(price) * 1.3, 2)
        else:
            new_data["standard_price"] = 4500  #如果价格没找到就给个初始值
        # 父SKU
        new_data["parent_sku"] = shein_data.iloc[0]["sku"]
        # TODO: 五点和材质  <29-12-21, yuzhe> #
        # TODO: 颜色尺码  <29-12-21, yuzhe> #

    new_data["item_sku"] = row['sku']
    new_data["item_name"] = row['title']
    try:
        # 成分, 有两种表达方式
        new_data["outer_material_type"] = dict_bullet["材料"]
        new_data["material_composition"] = dict_bullet["成分"]
    except Exception as e:
        new_data["outer_material_type"] = dict_bullet["ファブリック"]
        new_data["material_composition"] = dict_bullet["ファブリック"]
    # 衣门襟
    # .get 方法,如果没找到值,就返回None
    new_data["closure_type"] = dict_bullet.get("プラケット-タイプ")
    # 衣领
    new_data["neck_style"] = dict_bullet.get("ネックライン")
    new_data["collar_style"] = dict_bullet.get("ネックライン")
    # 风格
    new_data["lifestyle"] = dict_bullet.get("スタイル")
    new_data["style_keywords"] = dict_bullet.get("スタイル")
    # 季节
    new_data["seasons"] = dict_bullet.get("シーズン")
    # 袖型
    new_data["sleeve_type"] = dict_bullet.get("袖丈")

    new_data["product_description"] = row['description']
    # new_data["outer_material_type"] = row['']
    new_data["main_image_url"] = row['image1']
    new_data["other_image_url1"] = row['image2']
    new_data["other_image_url2"] = row['image3']
    new_data["other_image_url3"] = row['image4']
    new_data["other_image_url4"] = row['image5']
    new_data["other_image_url5"] = row['image6']
    new_data["other_image_url6"] = row['image7']
    new_data["other_image_url7"] = row['image8']
    if str(shein_data.iloc[1]["color"]) == "nan":
        new_data["variation_theme"] = "Size"
    else:
        new_data["variation_theme"] = "SizeColor"
    new_data["part_number"] = row['sku']
    new_data["product_description"] = row['description']
    new_data["model"] = row['sku']
    # new_datas = pd.concat([new_datas, new_data], axis = 0, ignore_index=True)
    new_datas = new_datas.append(new_data, ignore_index=True)
    # ic(new_datas)
# 插回原来表头 之前head =2
def Write2listing(new_datas):
    new_datas.columns = headers.columns
    new_datas = headers.append(new_datas, ignore_index=True)
    writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')
    new_datas.to_excel(writer, index=False)
    writer.close()
# %%
