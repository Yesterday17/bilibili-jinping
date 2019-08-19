import time
import os.path
import random
import requests
from multiprocessing import Pool

latest_aid = 64399007  # till Mon Aug 19 2019 13:50:56 GMT+0800 (中国标准时间)
concurrent = 16
proxy_list = []
proxy_authorization = ''
user_agent_list = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
    # iPhone 6：
    "Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25",
]


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
    reason_list = []
    simple_word_list = [
        str(2 ** 6 + 2 ** 4 + 2 ** 3 + 2 ** 0), str(2 ** 6),
        '\u5929\u5b89\u95e8', '\u957f\u5b89\u8857', '\u5766\u514b',
        '\u6cfd', '\u86d9', '\u86e4', '\u771f\u6b63\u7684\u7c89\u4e1d', '\u9ed1\u6846\u773c\u955c',
        '\u7ee7\u5f80\u5f00\u6765', '\u4ed6\u6539\u53d8\u4e86\u4e2d\u56fd', '\u4ed6\u53c8\u6539\u56de\u53bb\u4e86',
        '\u5750\u4e95\u89c2\u5929', '\u87b3\u81c2', '\u87b3\u81c2\u5f53\u8f66', '\u87b3\u81c2\u6321\u8f66',
        '\u7ef4\u5c3c', '\u718a', '\u6076\u4e60', '\u964b\u4e60',
        '\u5305', '\u5305\u5b50', '\u5e86\u4e30',
        '\u5cbf\u7136\u4e0d\u52a8',
        '\u5012', '\u5012\u8f66', '\u5012\u653e',
        '\u8428\u683c\u5c14', '\u683c\u8428\u5c14',
        '\u6e05\u5173', '\u6613\u9053', '\u901a\u5546', '\u5bbd\u8863', '\u5bbd\u519c',
        '\u7cbe\u6e5b', '\u7cbe\u751a', '\u7ec6\u817b', '\u5de5\u7b14\u753b',
        '\u4eba\u5747', '\u516b\u5343\u4e07',
        '\u5929\u884c\u5065', '\u4e0d\u5f3a\u81ea\u606f', '\u81ea\u5f3a\u4e0d\u606f',
        '\u91d1\u79d1\u5f8b\u7389', '\u91d1\u79d1\u7389\u5f8b',
        '\u6cfc\u58a8',
        '\u4e00\u672c\u8d26', '\u95f9\u5f97\u6b22', '\u62c9\u6e05\u5355',
        '\u4e09\u5c3a', '\u795e\u660e', '\u5e94\u9a8c',
        '200\u65a4', '\u4e8c\u767e\u65a4', '10\u91cc', '\u5341\u91cc',
        '\u5c71\u8def', '\u6362\u80a9', '\u55b7\u7caa',
        '\u8881\u4e16\u51ef', '\u7687\u5e1d', '\u79f0\u5e1d', '\u6e05\u671d',
        '\u8d75',
        # B站不管下面这个
        '\u9761\u9761\u4e4b\u97f3', '\u7ea2\u6b4c', '\u8f7b\u6b4c\u66fc\u821e', '\u8c6a\u8fc8', '\u79e6\u57ce'
    ]

    related_word_list = [
        ['\u8fea\u58eb\u5c3c', '\u89c6\u9891\u4e2d\u53ef\u80fd\u542b\u6709\u7ef4\u5c3c\u718a']
    ]

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
    if os.path.exists('result/start.txt'):
        file = open('result/start.txt', 'r')
        start = int(file.readline())
        file.close()
    return start


def update_start(aid):
    file = open('result/start.txt', 'w')
    file.write(str(aid))
    file.close()


def encode(to_encode=''):
    return to_encode.encode('ascii', 'xmlcharrefreplace').decode('ascii')


def write_file(aid, reply, info):
    print('[INFO] av%d disabled comment' % aid)
    file = open('result/%d.md' % aid, 'w')

    def write(content, to_encode=True):
        if to_encode:
            return file.write(encode(content))
        else:
            return file.write(content)

    write('# 报告: av%d\n\n' % aid)

    write('## 基本信息\n')
    write('### 标题\n%s  \n' % info['data']['title'])
    write('### 简介\n```\n')
    write(info['data']['desc'], False)
    write('\n```\n')
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
