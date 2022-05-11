import datetime
import binascii  # 二进制和ASCII码之间的转换
import Crypto.Random
from Crypto.PublicKey import RSA


class Student:
    Name = ""
    Credits = 20.0

    def __init__(self):
        # 生成公钥和私钥
        random = Crypto.Random.new().read
        self._private_key = RSA.generate(1024, random)
        self._public_key = self._private_key.publickey()
        # 利用公钥的ASCII码当作用户名
        self.Name = binascii.hexlify(self._public_key.exportKey(format="DER")).decode(
            "ascii"
        )


class Transaction:
    def __init__(self, sender, recipient, value):
        if sender.Credits > value:
            sender.Credits -= value
            recipient.Credits += value
            self.time = datetime.datetime.now()
            print("Transaction finished at %s" % (self.time))
        else:
            print("You need much more money!Transaction failed!!")


def main():
    StuA = Student()
    StuB = Student()
    tran = Transaction(StuA, StuB, 10)

    print("Student: %s has %f credits" % (StuA.Name, StuA.Credits))
    print("Student: %s has %f credits" % (StuB.Name, StuB.Credits))


if __name__ == "__main__":
    main()
