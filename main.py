import datetime
import binascii  # 二进制和ASCII码之间的转换
import Crypto.Random
from Crypto.PublicKey import RSA

import os
import hashlib #用于hash计算

import configparser  # 处理ini文件
from Crypto.Signature import PKCS1_v1_5 #用于签名
from Crypto.Hash import SHA #用于签名

class Student:
    Name = ""
    Credits = 20.0
    private_key = '' #修改为可以外部访问
    public_key = ''  #修改为可以外部访问

    def __init__(self, stuName):
        PrivateFile = "%s_Private.pem" % (stuName)
        if os.path.exists(PrivateFile):
            self.private_key = self.import_Account(PrivateFile)
        else:
            random = Crypto.Random.new().read
            # 生成私钥
            self.private_key = RSA.generate(1024, random)
            self.export_Account(PrivateFile, self.private_key)

        publickFile = "%s_Public.pem" % (stuName)
        if os.path.exists(publickFile):
            self.public_key = self.import_Account(publickFile)
        else:
            # 生成公钥
            self.public_key = self.private_key.publickey()
            self.export_Account(self.public_key)

        # 计算出账户
        str1 = binascii.hexlify(self.public_key.exportKey(format="DER")).decode(
            "ascii"
        )
        str2 = hashlib.sha256(str1.encode("utf-8")).hexdigest()
        str3 = hashlib.sha256(str2.encode("utf-8")).hexdigest()
        self.Name = str3
        print("Account is ready: %s" % (self.Name))

    def export_Account(self, accountNamePemStr, key):
        privatePemStr = key.exportKey()
        with open(accountNamePemStr, "wb") as f:
            f.write(privatePemStr)
            f.close()

    def import_Account(self, key):
        with open(key, "rb") as f:
            publicPemStr = f.read()
            key = Crypto.PublicKey.RSA.importKey(publicPemStr)
        return key


class Transaction:
    iniFileName = "Account.ini"

    def __init__(self,stu):
        self._private_key = stu.private_key
        self._private_key_str = binascii.hexlify(self._private_key.exportKey(format='DER')).decode('ascii')
        self._public_key = stu.public_key
        self._public_key_str = binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')
        return

    def Transfer(self, sender, recipient, value):
        '''C7没有解决余额不足也会进行交易的问题'''
        sender.Credits = self.AccountGet(sender)
        recipient.Credits = self.AccountGet(recipient)
        if sender.Credits > value:
            sender.Credits -= value
            recipient.Credits += value
            self.time = datetime.datetime.now()
            print("Transaction finished at %s" % (self.time))
        self.AccountSave(sender)
        self.AccountSave(recipient)
        
        tranDetailStr = "sender:%s,recipient:%s,value:%.8f,time:%s" % (sender.Name,recipient.Name,value,self.time)
        signStr = self.SignTransaction(tranDetailStr)
        str1 = "%s,signstr:%s,pubkey:%s\n\n" % (tranDetailStr,signStr,self._public_key_str)
        self.TransactionSave(str1)
        return 

    def AccountGet(self, Stu):  # 存储账户余额信息
        cred = Stu.Credits
        config = configparser.ConfigParser()
        config.read(self.iniFileName, encoding="utf-8")
        list = config.sections()  # 获取到配置文件中所有分组名称
        if Stu.Name in list:  # 如果分组存在
            cred = config.getfloat(Stu.Name, "Credits")
        return cred

    def AccountSave(self, Stu):  # 存储账户余额信息
        config = configparser.ConfigParser()
        config.read(self.iniFileName, encoding="utf-8")
        list = config.sections()  # 获取到配置文件中所有分组名称
        if Stu.Name not in list:  # 如果分组不存在
            config.add_section(Stu.Name)  # 增加section
        config.set(Stu.Name, "Credits", str(Stu.Credits))
        with open(self.iniFileName, "w+") as f:
            config.write(f)
            f.close()
        return

    def TransactionSave(self, tranStr): #存储交易信息
        txtFileName = 'TranscationLists.txt'
        f = open(txtFileName, "a+")
        f.write(tranStr)
        f.close()
        return
    
    def SignTransaction(self,tranStr=''): #返回签名后的字符串
        signer = PKCS1_v1_5.new(self._private_key)
        h = SHA.new(tranStr.encode('utf8'))
        str2 = binascii.hexlify(signer.sign(h)).decode('ascii')
        return str2
    

def main():
    StuA = Student("A")
    StuB = Student("B")
    tran = Transaction(StuA)    # StuA发起的交易
    tran.Transfer(StuA, StuB, 10)

    print("Student: %s has %f credits" % (StuA.Name, StuA.Credits))
    print("Student: %s has %f credits" % (StuB.Name, StuB.Credits))


if __name__ == "__main__":
    iniFileName = "Account.ini" #用于存储账户余额
    txtFileName = 'TranscationLists.txt' #用于存储交易信息
    TransactionList = [] #用来存储所有的交易信息
    main()
