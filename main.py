import time
import os.path
import random
import requests
import sys
from multiprocessing import Pool
from settings import *


def json_get(url):
    try:
        proxy_addr = 'http://%s' % random.choice(proxy_list)
        req = requests.get(url, headers={
            'Proxy-Authorization': proxy_authorization,
            'Host': 'api.bilibili.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': random.choice(user_agent_list),
            'DNT': '1'
        }, proxies={'http': proxy_addr}, timeout=(3.0, 8.0))

        if req.status_code == 200:
            return req.json()
        else:
            print('[Error] %d, %s' % (req.status_code, url))
            print('[Server] %s' % proxy_addr)
            proxy_list.remove(proxy_addr)
            return json_get(url)
    except:
        return json_get(url)


def video_stat(aid):
    url = 'http://api.bilibili.com/x/web-interface/archive/stat?aid=%d' % aid
    return json_get(url)


def video_reply(aid):
    url = 'http://api.bilibili.com/x/v2/reply?pn=1&ps=1&type=1&oid=%d' % aid
    return json_get(url)


def video_info(aid):
    url = 'http://api.bilibili.com/x/web-interface/view?aid=%d' % aid
    return json_get(url)


def guess_reason(aid, info):
    # from word_list import *
    from word_list_encoded import *

    reason_list = []

    if simple_word_list[0] in str(aid) or simple_word_list[1] in str(aid):
        reason_list.append('aid 中含有 %s 或 %s' % (simple_word_list[0], simple_word_list[1]))

    for word in simple_word_list:
        if word in info['data']['title']:
            reason_list.append('标题中含有 %s' % word)

    for word in related_word_list:
        if word[0] in info['data']['title']:
            reason_list.append(('标题中含有 %s, %s' % (word[0], word[1])))

    if len(reason_list) == 0:
        reason_list.append('未找到原因, 请自行分析')

    return reason_list


def read_start():
    start = 2
    if os.path.exists('docs/start.txt'):
        file = open('docs/start.txt', 'r')
        start = int(file.readline())
        file.close()
    return start


def update_start(aid):
    file = open('docs/start.txt', 'w')
    file.write(str(aid))
    file.close()


def encode(to_encode=''):
    return to_encode.encode('ascii', 'xmlcharrefreplace').decode('ascii')


def write_file(aid, reply, info):
    print('[INFO] av%d disabled comment' % aid)
    file = open('docs/%d.md' % aid, 'w')

    def write(content, to_encode=True):
        if to_encode:
            return file.write(encode(content))
        else:
            return file.write(content)

    write('# 报告: av%d\n\n' % aid)

    write('## 基本信息\n')
    write('### 标题\n%s  \n' % info['data']['title'])
    write('### 简介\n%s  \n' % info['data']['desc'].replace('\n', '  \n'))
    write('### UP\n[%s](https://space.bilibili.com/%d)  \n' % (
        info['data']['owner']['name'], info['data']['owner']['mid']))
    write('### 投稿时间\n%s  \n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['data']['pubdate'])))
    write('### 链接\nhttps://www.bilibili.com/av%d  \n' % aid)
    write('\n')

    write('## 评论信息\n')
    write('### 评论返回代码\n%d  \n' % reply['code'])
    write('### 评论返回信息\n%s  \n' % reply['message'])
    write('\n')

    write('## 推断\u7981\u8bc4原因\n')
    for reason in guess_reason(aid, info):
        write('- %s  \n' % reason)
    write('\n')

    file.close()


def main_work(aid):
    # 检查视频是否存在
    stat = video_stat(aid)
    if stat['code'] != 0:
        # 视频已删除/下架
        print('[INFO] av%d not available' % aid)
        return

    # 检查评论区情况
    reply = video_reply(aid)
    if reply['code'] == 0:
        # 评论区正常
        print('[INFO] av%d comment open' % aid)
        return

    # 获取视频详细信息
    info = video_info(aid)
    if info['code'] != 0:
        # 没遇见过
        print(info)
        return

    # 写入文件
    write_file(aid, reply, info)


def main():
    # 单纯的下载模式
    if len(sys.argv) > 1:
        with Pool(16) as p:
            p.map(main_work, map(lambda x: int(x), sys.argv[1:]))
        return

    aid = read_start()
    while aid <= latest_aid:
        range_end = min(aid + concurrent, latest_aid + 1)
        with Pool(16) as p:
            p.map(main_work, list(range(aid, range_end)))

        # 更新 aid
        aid = range_end
        update_start(aid)


if __name__ == '__main__':
    main()
