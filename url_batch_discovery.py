import request
import os
import sys
import time
import json
import requests
import datetime
import argparse
import threading
import pandas as pd

def shengyu(tmp_url_file, subdoamin_url_file):
    while (global_num == 0):
        if os.path.exists(tmp_url_file):
            with open(tmp_url_file) as tmp_f:
                tmp_f = tmp_f.readlines()
                tmp_f_len = len(tmp_f)
                if tmp_f_len > 1:
                    current_url = json.loads(tmp_f[-1])['url'].split('//')[1].split(':')[0].strip()
                    with open(subdoamin_url_file) as subdomain_f:
                        subdomain_f = subdomain_f.readlines()
                        num = 0
                        for i in subdomain_f:
                            num = num + 1
                            i = i.strip().replace('\n', '')
                            if '//' in i:
                                i = i.split('//')[1]
                            elif ':' in i:
                                i = i.split(':')[0]
                            if i == current_url:
                                tmp_len_path = './tmp/tmp_len.txt'
                                if os.path.exists(tmp_len_path):
                                    current_row = num
                                    huoqu_rate = float('%.2f' % (current_row / len(subdomain_f) * 100))
                                    with open(tmp_len_path) as len_f:
                                        len_f = float(len_f.read().replace('\n', ''))
                                        if huoqu_rate > len_f:
                                            shengyu_row = len(subdomain_f) - num
                                            with open(tmp_len_path, 'w') as w:
                                                w.write(str(huoqu_rate))
                                            current_time = datetime.datetime.now().strftime('%H:%M:%S')
                                            print('\033[1;33m[%s] 剩余%s行，已检测%s行，检测到%s条结果，完成进度%s，最新获取URL：%s\033[0m' % (
                                                current_time, shengyu_row, current_row, tmp_f_len,
                                                str(huoqu_rate) + '%',
                                                current_url))
                                else:
                                    current_row = num
                                    shengyu_row = len(subdomain_f) - num
                                    huoqu_rate = '%.2f' % (current_row / len(subdomain_f) * 100)
                                    with open(tmp_len_path, 'w') as w:
                                        w.write(str(huoqu_rate))
                                    current_time = datetime.datetime.now().strftime('%H:%M:%S')
                                    print('\033[1;33m[%s] 剩余%s行，已检测%s行，检测到%s条结果，完成进度%s，最新获取URL：%s\033[0m' % (
                                        current_time, shengyu_row, current_row, tmp_f_len, str(huoqu_rate) + '%',
                                        current_url))
        time.sleep(3)


def clear_url(file):
    clear_url_list = []
    with open(file) as f:
        f = f.readlines()
        for i in f:
            i = i.strip()
            if '//' in i:
                i = i.split('/')[2]
            elif '/' in i:
                i = i.split('/')[0]
            clear_url_list.append(i)
    with open('./tmp/clear_url.txt', 'w') as w:
        for i in clear_url_list:
            w.write(i + '\n')


def main(file, match_string, output_path, ports, threads):
    print('''\033[1;34m[!] 扫描线程：%s
[!] 导出目录：%s
[!] 待扫描文件：%s
[!] 待扫描端口：%s
[!] 待匹配字符串：%s
\033[0m''' % (threads, output_path, file, ports, match_string))
    if file == './tmp/tmp.txt':
        with open(file) as f:
            file_url = f.readlines()[0]
    else:
        file_url = file
    if len(file_url.split('/')) > 2 and '//' not in file_url:
        file_title = output_path + file_url.split('/')[-1].split('.')[-2] + '_tmp.txt'
        file_path = output_path + file_url.split('/')[-1].split('.')[-2] + '.xlsx'
    elif len(file_url.split('/')) > 2 and '//' in file_url:
        file_url = file_url.strip('/')
        file_title = output_path + file_url.split('/')[-1].replace('.', '_') + '_tmp.txt'
        file_path = output_path + file_url.split('/')[-1].replace('.', '_') + '.xlsx'
    else:
        file_title = output_path + file_url.replace('.', '_') + '_tmp.txt'
        file_path = output_path + file_url.replace('.', '_') + '.xlsx'
    global global_num
    global_num = 0
    t = threading.Thread(target=shengyu, args=(file_title, './tmp/clear_url.txt',))
    t.start()
    pool = []
    clear_url(file)
    if match_string == 'null':
        os.system('httpx -l ./tmp/clear_url.txt -threads %s -title -title -json -silent -ports %s -follow-redirects > %s' % (threads, ports, file_title))
        #os.system('httpx -l ./tmp/clear_url.txt -threads %s -title -title -json -silent -follow-redirects > %s' % (threads, file_title))
    else:
        os.system(
            'httpx -l ./tmp/clear_url.txt -threads %s -title -title -json -silent -ports %s -match-string "%s" -follow-redirects > %s' % (
                threads, ports, match_string, file_title))
    os.remove('./tmp/clear_url.txt')
    with open(file_title) as f:
        f = f.readlines()
        for i in f:
            i = json.loads(i.replace('\n', ''))
            info = {}
            info['url'] = i['url']
            info['title'] = i['title']
            info['webserver'] = i['webserver']
            info['status-code'] = i['status-code']
            info['ip'] = i['ip']
            info['content-length'] = i['content-length']
            info['response-time'] = i['response-time']
            pool.append(info)

    df = pd.DataFrame(pool)
    os.remove(file_title)
    global_num = 1
    if os.path.exists('./tmp/tmp_len.txt'):
        os.remove('./tmp/tmp_len.txt')
    if len(pool) == 0:
        print('\033[1;31m\n[-] 未获取到数据\033[0m')
    else:
        df.to_excel(file_path,
                    columns=['url', 'title', 'webserver', 'status-code', 'ip', 'content-length', 'response-time'],
                    index=False, encoding='utf_8_sig')
        print('\033[1;32m\n[+] 数据获取完毕，已导出到 %s \033[0m' % file_path)


if __name__ == '__main__':
    print('''\033[1;34m                                                                      
 _____ _____ __       _____     _       _      ____  _                             
|  |  | __  |  |     | __  |___| |_ ___| |_   |    \|_|___ ___ ___ _ _ ___ ___ _ _ 
|  |  |    -|  |__   | __ -| .'|  _|  _|   |  |  |  | |_ -|  _| . | | | -_|  _| | |
|_____|__|__|_____|  |_____|__,|_| |___|_|_|  |____/|_|___|___|___|\_/|___|_| |_  |
                                                                              |___|
 Version: 0.4               date: 2021.1.14
 公众号：TeamsSix           博客：teamssix.com
 Author: TeamsSix           GitHub：https://github.com/teamssix/url_batch_discovery
 注：本工具核心功能来自于优秀的 httpx 工具，使用本工具需要先安装 httpx，httpx 项目地址：https://github.com/projectdiscovery/httpx
\033[0m''')
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', dest='list', help='指定URL列表文件')
    parser.add_argument('-m', dest='match', help='指定要匹配的关键字，返回结果中将只包含存在该关键字的内容')
    parser.add_argument('-o', dest='output', help='导出的文件路径，默认保存在./output/文件夹内，导出文件格式为xlsx，格式：/path1/path2/')
    parser.add_argument('-p', dest='port', help='指定要检测的端口，默认80和443端口，格式：80,443,8000-8010')
    parser.add_argument('-t', dest='threads', help='指定线程大小，默认100个线程')
    parser.add_argument('-u', dest='url', help='指定单个URL')
    args = parser.parse_args()

    if not os.path.exists('./output'):
        os.makedirs('./output')

    if not args.list and not args.url:
        print('\033[1;31m[-] 未指定要访问的 URL 或者 URL 列表，帮助信息如下：\n\033[0m')
        parser.print_help()
        sys.exit()

    if args.match:
        match_string = args.match
    else:
        match_string = 'null'

    if args.output:
        output_path = args.output
        if not os.path.exists(args.output):
            print('\033[1;31m[-] 系统中未找到 %s 路径，请确认后再次执行。\n\033[0m' % output_path)
            sys.exit()
    else:
        output_path = './output/'

    if args.port:
        ports = args.port
    else:
        ports = '80,81,443,3000,7001,7443,8080,8443,8843,8888'

    if args.threads:
        threads = args.threads
    else:
        threads = '100'
    if not os.path.exists('./tmp'):
        os.makedirs('./tmp')
    if args.url:
        url = args.url
        with open('./tmp/tmp.txt', 'w') as w:
            w.write(url)
        main('./tmp/tmp.txt', match_string, output_path, ports, threads)
        os.remove('./tmp/tmp.txt')
    elif args.list:
        file = args.list
        if not os.path.isfile(file):
            print('\033[1;31m[-] 系统中未找到 %s 文件，请确认后再次执行。\n\033[0m' % file)
            sys.exit()
        else:
            with open(file) as f:
                f = f.readlines()
                if len(f) == 0:
                    print('\033[1;31m[-] %s 文件中貌似没有数据，请确认后再次执行。\n\033[0m' % file)
                    sys.exit()
                else:
                    main(file, match_string, output_path, ports, threads)
    os.removedirs('./tmp/')
