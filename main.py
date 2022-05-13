import datetime
import binascii  # 二进制和ASCII码之间的转换
import Crypto.Random
from Crypto.PublicKey import RSA

import os
import hashlib

import configparser  # 处理ini文件


class Student:
    Name = ""
    Credits = 20.0
    _private_key = ""
    _public_key = ""

    def __init__(self, stuName):
        """_summary_: 初始化学生账户

        如果存在账户私钥文件，则导入账户私钥；
        如果不存在账户私钥文件，则创建新的账户。
        导入和生成使用Crpyto库中的RSA算法。

        Args:
            stuName (_type_): 存储学生私钥的文件名
        """
        PrivateFile = "%s_Private.pem" % (stuName)
        if os.path.exists(PrivateFile):
            self._private_key = self.import_Account(PrivateFile)
        else:
            random = Crypto.Random.new().read
            # 生成私钥
            self._private_key = RSA.generate(1024, random)
            self.export_Account(PrivateFile, self._private_key)

        publickFile = "%s_Public.pem" % (stuName)
        if os.path.exists(publickFile):
            self._public_key = self.import_Account(publickFile)
        else:
            # 生成公钥
            self._public_key = self._private_key.publickey()
            self.export_Account(self._public_key)

        # 计算出账户
        str1 = binascii.hexlify(self._public_key.exportKey(format="DER")).decode(
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

    def __init__(self):
        return

    def Transfer(self, sender, recipient, value):
        sender.Credits = self.AccountGet(sender)
        recipient.Credits = self.AccountGet(recipient)
        if sender.Credits > value:
            sender.Credits -= value
            recipient.Credits += value
            self.time = datetime.datetime.now()
            print("Transaction finished at %s" % (self.time))
        self.AccountSave(sender)
        self.AccountSave(recipient)
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


def main():
    StuA = Student("A")
    StuB = Student("B")
    tran = Transaction()
    tran.Transfer(StuA, StuB, 10)

    print("Student: %s has %f credits" % (StuA.Name, StuA.Credits))
    print("Student: %s has %f credits" % (StuB.Name, StuB.Credits))


if __name__ == "__main__":
    main()
