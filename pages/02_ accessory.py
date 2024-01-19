import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2 import service_account


# @st.cache_resource

def load_data_csv(equipment):
    #sobiフォルダからのデータの読み込み
    df_ssr = pd.read_csv("sobi/ssr_" + equipment + ".csv")
    df_ksr = pd.read_csv("sobi/ksr_" + equipment + ".csv")
    # シートデータを結合して1つのDataFrameにする
    df = pd.concat([df_ksr, df_ssr])
    return df


df_ori = load_data_csv('accessory')
df = df_ori.copy()
df_reloaded = df.copy()

df_category_ori = pd.read_csv("sobi/ability-category.csv")
df_category = df_category_ori.copy()

output = df_reloaded.copy()
df_status = df_reloaded.copy()

#本番output,df_statusで置き換えることで,Noneが出力しないようにしてる
df_status.replace("" ,np.nan ,inplace=True)

submit_btn1 = st.radio("レアリティ", ("絞る", "絞らない"), index=1,key=31)

rare_filter = None
rare_list = []

if submit_btn1 == "絞る":
    # check box
    col = st.columns(2)
    ksr = col[0].checkbox(label='KSR')
    ssr = col[1].checkbox(label='SSR')

    if ksr:
        rare_list.append('KSR')
    if ssr:
        rare_list.append('SSR')
    # 条件が選択されている場合だけ、outputを条件に合致するレコードだけのDFに置き換える
    if ksr or ssr:
        rare_filter = df['レアリティ'].isin(rare_list)
        output = df[rare_filter]
        df_status = df_status[rare_filter]
submit_btn2 = st.radio("ステータス", ("絞る", "絞らない"), index=1,key=32)

status = True
if submit_btn2 == "絞る":
    # check box
    col = st.columns(6)
    hp = col[0].checkbox(label='体力')

    attack = col[1].checkbox(label='攻撃力')

    defense = col[2].checkbox(label='防御力')
    
    critical = col[3].checkbox(label='会心率')

    avoidance = col[4].checkbox(label='回避率')

    hit = col[5].checkbox(label='命中率')

    if hp:
        status = status & (df_status['体力'] > 0)
    
    if attack:
        status = status & (df_status['攻撃力'] > 0)
    
    if defense:
        status = status & (df_status['防御力'] > 0)

    if critical:
        status = status & (df_status['会心率'] > 0)

    if avoidance:
        status = status & (df_status['回避率'] > 0)

    if hit:
        status = status & (df_status['命中率'] > 0)
    # 条件が選択されている場合だけ、outputを条件に合致するレコードだけのDFに置き換える
    if hp or attack or defense or critical or avoidance or hit:
        output = output[status]

submit_btn3 = st.radio("アビリティ", ("絞る", "絞らない"), index=1,key=33)
#アビリティフィルタ
# アビリティ名のリストを作成
ability_name_list = df_category['アビリティカテゴリ分類'].unique()
# Nanを削除
ability_name_list = ability_name_list[1:]

if submit_btn3 == "絞る":
    #複数選択
    type_color3 = st.multiselect('アビリティ種類',(ability_name_list))
    if type_color3:
        # 選択されたアビリティが含まれている行を抽出
        ability_filter = output['アビリティカテゴリ'].apply(lambda x: any(ab in x for ab in type_color3) if pd.notnull(x) else False)

        output = output[ability_filter]

    
# outputが空でないならソートを実行
if not output.empty:
    output = output.sort_values('装備番号')
    output = output.reset_index(drop=True)  # インデックスをリセット
    output = output.drop(columns =['装備番号','レアリティ','アビリティカテゴリ'])

# 装備名のカラムを含める
# output_columns = output.columns.tolist()
# output = output[output_columns]
# output = output.replace(np.nan ,'')
st.write(output)
