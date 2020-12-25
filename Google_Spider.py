# -*- coding:utf-8 -*-
from gevent import monkey;monkey.patch_all()
from colorama import init,Fore
from multiprocessing import Process
from bs4 import BeautifulSoup
import gevent
import asyncio
import random
import time
import requests
import os
import re
'''
基于"site:{domain} inurl:** intext:** "的google搜索工具；
'''

init(wrap=True)  #在windows系统终端输出颜色要使用init(wrap=True)
class Google_query(object):
    def __init__(self):
        self.timeout=3
        self.calc=0
        self.url='/search?q={search}&btnG=Search&safe=active&gbv=1'

        self.Google_domain=[]
        #self.search=['site:{domain} inurl:upload','site:{domain} inurl:admin']
        self.search = ['site:{domain} inurl:admin','site:{domain} inurl:upload']
        self.target_domain=[]
        self.Proxies_ip=[]
        self.coroutine=[]
        self.ua=[]
        self.header=[]

    def google_search(self,ua,url,proxies,sleep):
        try:
            time.sleep(int(sleep))
            resp=requests.get(url=url,headers={'user-agent':ua},proxies=proxies,allow_redirects=False,timeout=30)
            if '302 Moved' in resp.text:
                print(Fore.YELLOW + '[!] ' + Fore.WHITE + '发现Google验证码！！！')
                exit()
            else:
                soap = BeautifulSoup(resp.text, 'html.parser')
                soap = soap.find_all("a")
                self.handle(soap,url)

        except Exception as r:
            print(Fore.RED+'[-] '+Fore.WHITE+'Error {}'.format(r))

    # 结果处理
    def handle(self,soap,url):
        count=0
        for data in soap:
            res1 = "/url?q"
            res2 = str(data.get('href'))

            if (res1 in res2):

                title=data.find('span')
                result = re.findall(".*>(.*)<.*", str(title))
                if title==None:
                    break;
                for x in result:
                    title=x
                url=res2.replace('/url?q=', '')
                head, middle, behind = url.partition('&sa')   #去除多余查询字符串
                print(Fore.GREEN + '[+] ' + Fore.WHITE + 'URL:{} title:{}'.format(
                    head, title))
                # 写入文件
                print('URL:{} title:{}'.format(head, title),
                      file=open('result/save.txt', 'a', encoding='utf-8'))
                count+=1
        if count == 1:
            print('找不到和您查询的: {}相符的内容或信息'.format(url))
        else:
            print(Fore.GREEN + '[*] ' + Fore.WHITE + '链接数量:{} 请求的url:{}'.format(count, url))

    # 构造请求
    def Build_Request(self,data):
        for y in data:
            for x in self.search:
                url='https://'+random.choice(self.Google_domain)+self.url.format(search=str(x).format(domain=y['target_domain']))
                #创建一个普通的Greenlet对象并切换
                self.coroutine.append(gevent.spawn(self.google_search,ua=y['user-agent'],url=url,proxies=y['proxies'],sleep=y['sleep']))

        #将协程任务添加到事件循环，接收一个任务列表
        gevent.joinall(self.coroutine)
        self.coroutine.clear()

    def Do_query(self):
        data={}
        domain_number=len(self.target_domain)
        if(domain_number==0):
            print(Fore.YELLOW + '[!] ' + Fore.WHITE + '目标domain为空，请赋值！！')
            exit()
        for x in range(domain_number):
            if self.calc==100:
                p=Process(target=self.Build_Request, args=(self.header,))
                p.start()
                self.header.clear()
                self.calc=0
                data={}
            data['user-agent']=random.choice(self.ua)
            data['target_domain']=self.target_domain[x]
            data['proxies']={'http':'http://{}'.format(random.choice(self.Proxies_ip)),'https':'https://{}'.format(random.choice(self.Proxies_ip))}
            data['sleep']=random.choice([x for x in range(1,10)])
            self.header.append(data)
            data = {}
            self.calc+=1

        if len(self.header)>0:
            p = Process(target=self.Build_Request, args=(self.header,))
            p.start()
            self.header.clear()
            self.calc = 0
            data = {}

    def read_file(self,file):
        dk = open(file, 'r', encoding='utf-8')
        for d in dk.readlines():
            data="".join(d.split('\n'))
            yield data

    async def getfile(self):
        if os.path.exists('files/UA.txt') and os.path.exists('files/target_domain.txt') and os.path.exists('files/proxies.txt') and os.path.exists('files/Google_domain.txt'):
            print(Fore.BLUE+'[+] '+Fore.WHITE+'加载所需文件中...')
        else:
            print(Fore.RED+'[-] '+Fore.WHITE+'缺少所需文件..请填补文件')
            exit()

        print(Fore.GREEN+'[~] '+Fore.WHITE+'开始执行google hacking')

        for u in self.read_file('files/UA.txt'):
            self.ua.append(u)

        for t in self.read_file('files/target_domain.txt'):
            self.target_domain.append(t)

        for p in self.read_file('files/proxies.txt'):
            self.Proxies_ip.append(p)

        for g in self.read_file('files/Google_domain.txt'):
            self.Google_domain.append(g)

        self.Do_query()


if __name__ == '__main__':
    author_info = '''
                    *****************************************************                                                  
                    *                Code By littlebin404               *
                    *               Google Hacking Spider!              *                                                  
                    *****************************************************
    '''
    print(author_info)
    obj=Google_query()
    loop=asyncio.get_event_loop()
    tk=loop.create_task(obj.getfile())
    loop.run_until_complete(tk)