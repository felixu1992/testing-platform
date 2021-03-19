import hashlib
import json
import os
import time

import winrm
from threading import Thread

def func():
    # os.system('calc')
    os.popen('calc')

if __name__ == '__main__':
    # hl = hashlib.md5()
    # hl.update('devicegroup'.encode(encoding='utf-8'))
    # password = hl.hexdigest()
    # win = winrm.Session('http://192.168.8.246:5985/wsman', auth=('device', 'isyscore'))
    # r = win.run_cmd('dir')
    # r = win.run_cmd('robot -d D:\\ui-debug D:\\ui-auto-test\\案例层')
    # print(str(r.std_out, encoding='gbk'))
    # print(str(r.std_err, encoding='gbk'))
    # print(password)
    # s = '[{\'depend\': 0, \'step\': [\'data\', \'total\']}]'
    # obj = json.loads(s)
    # json.loads()
    # print(obj)
    # j = json.dumps([['code'], ['data', 'total']])
    # print(j)
    t = Thread(target=func, args={})
    t.start()
    # time.sleep(1)
    print('main')
