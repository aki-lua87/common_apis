import os
import requests
import json
import boto3
from bs4 import BeautifulSoup

TARGET_URL = 'https://hololive.hololivepro.com/talents'
BUCKET_NAME = os.environ['BUCKET_NAME']
FILE_PATH = 'hololive/talents.json'


def get_all_links():
    # HTMLファイルを開く
    # with open('1.html', 'r', encoding='utf-8') as f:
    #     contents = f.read()
    html_text = requests.get(TARGET_URL).text
    soup = BeautifulSoup(html_text, 'html.parser')
    # 特定のURLで始まる<a>タグを見つける
    links = soup.find_all('a', href=True)
    filtered_links = [link['href'] for link in links if link['href'].startswith('https://hololive.hololivepro.com/talents/')]
    # print(filtered_links)
    return filtered_links


def get_talent_info(url):
    # HTMLファイルを開く
    # with open('sirakami.html', 'r', encoding='utf-8') as f:
    #     contents = f.read()
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    tarent_info = {}
    # <div class="bg_box">を見つける
    div = soup.find('div', class_='bg_box')
    # <h1>要素を見つける
    h1 = div.find('h1')
    # <span>要素を見つける
    span = h1.find('span')
    # nameとen_nameを取得する
    name = h1.text.replace(span.text, '').strip()
    en_name = span.text.strip()
    # 結果を表示する
    tarent_info.update(name=name, en_name=en_name)
    # print(f'name: {name}, en_name: {en_name}')
    # <p class="catch">を見つける
    catch = soup.find('p', class_='catch').text.strip()
    # <p class="txt">を見つける
    txt = soup.find('p', class_='txt')
    # videoタグを削除する
    for video in txt.find_all('video'):
        video.decompose()
    txt = txt.text.replace('\n', '').replace('\r', '').strip()
    # <ul class="t_sns clearfix">内のYoutubeのURLを見つける
    youtube_url = soup.find('ul', class_='t_sns clearfix').find('a', href=True)['href']
    # <ul class="t_sns clearfix">のXのURLを見つける
    twitter_url = soup.find('ul', class_='t_sns clearfix').find('a', href=lambda x: x and x.startswith('https://twitter.com/'))['href']
    # 結果を表示する
    # print(f'catch: {catch}, txt: {txt}, youtube_url: {youtube_url}, twitter_url: {twitter_url}')
    tarent_info.update(catch=catch, txt=txt, youtube_url=youtube_url, twitter_url=twitter_url)
    # <div class="talent_data">を見つける
    div = soup.find('div', class_='talent_data')
    # <dt>と<dd>要素を見つける
    dt_elements = div.find_all('dt')
    dd_elements = div.find_all('dd')
    # <dt>要素のテキストをキーとし、<dd>要素のテキストを値とする辞書を作成する
    data = {dt.text.strip(): dd.text.replace('\n', '').replace('\r', '').replace(' ', '').strip() for dt, dd in zip(dt_elements, dd_elements)}
    # キーの日本語を可能な限り英語に変換するためにdataをループさせてキー名を取得する
    for key in list(data.keys()):
        # print(key)
        # キー名を変換する
        if key == 'ユニット':
            # ユニットの場合はスラッシュ区切りで複数の所属がある場合があるため、リストに変換する
            data['affiliation'] = data.pop(key).split('/')
            # data['affiliation'] = data.pop(key)
        elif key == '誕生日':
            data['birthday'] = data.pop(key)
        elif key == '身長':
            data['height'] = data.pop(key)
        elif key == 'デビュー日':
            data['debut'] = data.pop(key)
        elif key == '初配信日':
            data['first_live_date'] = data.pop(key)
        elif key == 'イラストレーター':
            data['illustrator'] = data.pop(key)
        elif key == 'ハッシュタグ':
            # いろいろなハッシュタグがあるけど共通化できなそうなので諦める
            data['hashtag'] = data.pop(key)
    tarent_info.update(data)
    # print(tarent_info)
    return tarent_info


# 文字列を受け取ってboto3を使ってS3へ保存する
def save_to_s3(bucket_name, key, content):
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, key).put(Body=content)


def main(event, context):
    urls = get_all_links()
    talents_info = []
    for url in urls:
        info = get_talent_info(url)
        talents_info.append(info)
    jsonstr = json.dumps(talents_info, ensure_ascii=False, indent=2)
    save_to_s3(BUCKET_NAME, FILE_PATH, jsonstr)
