# WeakpassScan
弱密码扫描工具

支持对ssh、postgresql、Redis、MySQL、mongoDB、FTP、sqlserver(mssql)、Dahua(大华)、hikvision(海康威视)进行弱密码扫描，共9个类别；
仓库代码参考：https://github.com/popmedd/SubDomainsResultDeal/blob/0303d95bd96b8f1e696c6534f686f30809763970/util/unauth/weakPassScan.py，在原代码的基础上增加到了9中弱密码扫描，并且修改了用户名-密码集合的使用方式，并将代码修改为python3

# 软件声明
  本工具仅用于测试学习，不可对真实设备进行使用，后果自负；

# Python版本
  Python3

# 使用方法
python weakpass_scan.py [type] -i [host] -p [port] -o [timeout] -t [thread]

​	type: 必选项，ssh or postgresql or redis or mysql or mongodb or ftp or sqlserver or mssql or dahua or hikvision

​	-i : 必选项，目标IP

​	-p : 必选项，目标端口

​	-o  : 超时时间，默认5秒

​	-t  : 线程数量，默认10



# 参考代码

https://github.com/popmedd/SubDomainsResultDeal/blob/0303d95bd96b8f1e696c6534f686f30809763970/util/unauth/weakPassScan.py

  

