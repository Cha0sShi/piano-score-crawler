# -*- coding:utf-8 -*-
from urllib import parse
import requests
from bs4 import BeautifulSoup
import os
from PIL import Image

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}


def get_scorelist_by_keyname(keyname):
    """
    从关键字获取乐谱数据
    :param keyname:
    :return:
    """

    # 循环请求多个页面示例
    url = 'https://www.everyonepiano.cn/Music-search/?word={}'
    parse_name = parse.quote(keyname)
    url = url.format(parse_name) + "&come=web"

    html = get_html_by_url(url, headers)
    soup = BeautifulSoup(html, 'html.parser')
    scorelist = get_scorelist_by_scorelistsoup(soup)

    # 如果是第一次寻找,并且还有其他页面,也递归寻找

    pagelist = soup.find('div', class_='pagelist')

    links = pagelist.find_all('a')

    for link in links:
        url_t = url + link.get('href')
        if url_t:
            html_t = get_html_by_url(url_t, headers)
            soup_t = BeautifulSoup(html_t, 'html.parser')
            scorelist += get_scorelist_by_scorelistsoup(soup_t)

    return scorelist


def get_html_by_url(url, headers):
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        response.encoding = "utf-8"
        html = response.text
    return html


def get_scorelist_by_scorelistsoup(soup):
    scorelist = []

    scoreblocks = soup.find_all('div', class_='MusicIndexBox')

    for score_block in scoreblocks:
        data = {
            'MIMusicNO': score_block.find('div', class_='MIMusicNO').text,
            'Title': score_block.find('a', class_='Title').text,
            'Times': score_block.find('span', class_="MIMusicInfo2Num").text,
        }
        scorelist.append(data)

    # 打印结果
    for block in scorelist:
        print("MIMusicNO:", block['MIMusicNO'])
        print("Title:", block['Title'])
        print("Times:", block['Times'])
        print("---")
    return scorelist


def get_and_save_scoreImage_by_id(id, title, type):
    url = "https://www.everyonepiano.cn/{}-{}.html".format(type, id)
    html = get_html_by_url(url, headers)
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img', class_='DownMusicPNG')
    img_link_list = [img['src'] for img in images]
    directory = 'score-image/{}/'.format(title)
    if not os.path.exists(directory):
        os.makedirs(directory)
    i = 1
    image_files = []
    for img_link in img_link_list:
        filename = '{}{}_{}{}.jpg'.format(directory, title, type, i)
        image = requests.get(url=("https://www.everyonepiano.cn" + img_link), headers=headers).content
        with open(filename, 'wb') as f:
            f.write(image)

            image_files.append(filename)
        i += 1

    # 拼接
    images = [Image.open(image_file) for image_file in image_files]
    total_width = images[0].width
    total_height = images[0].height*(i-1)

    result_image = Image.new("RGB", (total_width, total_height))
    y_offset = 0
    for image in images:
        result_image.paste(image, (0,y_offset))
        y_offset += image.height
    result_image.save(os.path.join(directory,"-竖版连接.jpg"))


