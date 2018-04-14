# -×- conding:utf=8 -*-

import requests
import re
import time
from bs4 import BeautifulSoup
import logging
from tables import *

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HduReptile():


    # 利用python爬虫爬取HDUOJ题目的正确代码，并且模拟提交

    def __init__(self, username, passwd, interval=15):

        self.username = username
        self.passwd = passwd
        self.interval = interval
        self.hdu_session = requests.Session()
        self.baidu_session = requests.Session()

        SessionCls = sessionmaker(bind=engine)
        self.db_session = SessionCls()

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                          '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        # submit 表单对应语言
        self.language_dict = {
            'G++': 0,
            'GCC': 1,
            'C++': 2,
            'C': 3,
            'Pascal': 4,
            'Java': 5,
            'C#': 6
        }
        self.hdu_session.headers.update(header)
        self.baidu_session.headers.update(header)

    def __login(self):

        # 爬虫模拟登录

        # 登录页面的url
        url = 'http://acm.hdu.edu.cn/userloginex.php?action=login'

        # 登录所需要填写的表单
        data = {
            'username': self.username,
            'userpass': self.passwd,
            'login': 'Sign In'
        }

        # 登录所需要添加的header
        headers = {
            'host': 'acm.hdu.edu.cn',
            'origin': 'http://acm.hdu.edu.cn',
            'referer': 'http://acm.hdu.edu.cn/'
        }
        try:
            self.hdu_session.post(url=url, headers=headers, data=data)
        except Exception as exe:
            logger.error('login fail', exe)

    def __submit(self, problemid, usercode, language):

        # 爬虫提交答案

        usercode = usercode.encode('utf-8').decode()
        url = 'http://acm.hdu.edu.cn/submit.php?action=submit'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'check': 0,
            'problemid': problemid,
            'language': self.language_dict[language],
            'usercode': usercode
        }

        logger.debug('submit problem ID: %s'%(problemid))

        try:
            self.hdu_session.post(url=url, headers=headers, data=data)
        except Exception as exc:
            logger.error('submit fail', exc)

    def __get_ac_code(self, problem_id):

        url = 'http://www.baidu.com/s?wd=hdu%20' + str(problem_id)

        # 百度搜索后的html页面
        res = self.baidu_session.get(url)

        # beautifulSoup解析对象
        soup = BeautifulSoup(res.text, 'html.parser')

        # 百度所得全部的链接
        dev_list = soup.find_all('a', attrs={'target': '_blank', 'class': 'c-showurl', 'style': 'text-decoration:none;'})

        # 目前从其中过滤得到 csdn的博客地址
        solution_list = []
        for item in dev_list:
            if item.text.find('blog.csdn.net') != -1:
                 solution_list.append(item['href'])

        # 获得该链接的博客
        for url in solution_list:
            res = self.baidu_session.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find('title')
            code = soup.find('pre', attrs={'class': 'cpp'})
            if code:
                # 对博客标题进行一个check
                if title.text.find(str(problem_id)) != -1:
                    logger.info("get problem %s code: "%(problem_id))
                    return code.text

        return None

    def __get_solve_list(self, username):

        # 获得已经AC的题目的列表
        url = r'http://acm.hdu.edu.cn/userstatus.php?user=' + username

        res = self.baidu_session.get(url)

        soup = BeautifulSoup(res.text, 'html.parser')

        solve_list_html = soup.find('p', align='left')

        #slove_list_html:  "p(1000,8,9);p(1001,2,2);"

        solve_list = solve_list_html.text.split(';')

        solve_ids = []
        for item in solve_list:
            if item:
                solve_ids.append(re.search(r'[0-9]{4}', item).group())
        return solve_ids

    def __update_db_status(self):

        # 更新数据库中AC题目的status

        query = self.db_session.query(HduAcCode)
        solve_ids = self.__get_solve_list(self.username)
        for problem_id in solve_ids:
            print(problem_id)
            query.filter(HduAcCode.problem_id == problem_id).update({HduAcCode.status: 1})
        self.db_session.commit()

    def run(self, start=1000, end=2000):
        self.__login()
        self.__update_db_status()
        for problem_id in range(start, end):

            code = self.__get_ac_code(problem_id)
            if not code:
                continue
            try:
                self.__submit(problemid=problem_id, usercode=code, language='G++')
            except Exception as exc:
                logger.error("reptile problem %s fail"%(problem_id))
            finally:
                problem = HduAcCode(problem_id=problem_id, code=code)
                self.db_session.add(problem)
                logger.info("reptile problem %s success"%(problem_id))
                self.db_session.commit()
            time.sleep(self.interval)



if __name__ == '__main__':

    foo = HduReptile(username, passwd, 10)
    foo.run()
