import hashlib

if __name__ == '__main__':
    hl = hashlib.md5()
    hl.update('123456'.encode(encoding='utf-8'))
    password = hl.hexdigest()
    print(password)