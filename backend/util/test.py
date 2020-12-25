import hashlib
import json

if __name__ == '__main__':
    # hl = hashlib.md5()
    # hl.update('123456'.encode(encoding='utf-8'))
    # password = hl.hexdigest()
    # print(password)
    # s = '[{\'depend\': 0, \'step\': [\'data\', \'total\']}]'
    # obj = json.loads(s)
    # json.loads()
    # print(obj)
    j = json.dumps([['code'], ['data', 'total']])
    print(j)
