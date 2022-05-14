import binascii
import os 
# following imports are required by PKI
import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 #用于签名
from Crypto.Hash import SHA #用于签名
import hashlib #用于hash计算
import configparser #处理ini文件
import time,datetime
import base64

class Student:
    Name = ''
    Credits = 20.0
    private_key = '' #修改为可以外部访问
    public_key = ''  #修改为可以外部访问
    def __init__(self,stuName):
        PrivateFile = "%s_Private.pem" % (stuName)
        if os.path.exists(PrivateFile):
            #导入已有账户的私钥
            with open(PrivateFile, "rb") as f:
                privatePemStr = f.read()
                self.private_key = Crypto.PublicKey.RSA.importKey(privatePemStr)
        else:
            #创建新的账户
            random = Crypto.Random.new().read
            self.private_key = RSA.generate(1024, random)
            # 保存密钥
            with open(PrivateFile, "wb") as f:
                privatePemStr = self.private_key.exportKey()   # 导出私钥
                f.write(privatePemStr)
                f.close()

        publickFile = "%s_Public.pem" % (stuName)
        if os.path.exists(publickFile):
            #导入已有账户的公钥
            with open(publickFile, "rb") as f:
                publicPemStr = f.read()
                self.public_key = Crypto.PublicKey.RSA.importKey(publicPemStr)
        else:
            self.public_key = self.private_key.publickey()
            publicPemStr = self.public_key.exportKey()   # 导出公钥
            with open(publickFile, "wb") as f:
                f.write(publicPemStr)
        #计算出账户
        str1 = self.public_key.exportKey(format='PEM').decode('utf-8')
        h1 = Crypto.Hash.SHA256.new(str1.encode('utf-8'))
        str2 = binascii.hexlify(h1.digest()).decode('utf-8')
        h2 = Crypto.Hash.SHA256.new(str2.encode('utf-8'))
        str3 = binascii.hexlify(h2.digest()).decode('utf-8')
        self.Name = str3.upper()
        print("Account is ready: %s" % (self.Name))

class Transaction:
    iniFileName = "Account.ini"
    def __init__(self,stu):
        self._private_key = stu.private_key
        #self._private_key_str = binascii.hexlify(self._private_key.exportKey(format='PEM')).decode('ascii')
        self._private_key_str = base64.b32encode(self._private_key.exportKey(format='PEM'))
        self._public_key = stu.public_key
        #self._public_key_str = binascii.hexlify(self._public_key.exportKey(format='PEM')).decode('ascii')
        self._public_key_str =base64.b32encode(self._public_key.exportKey(format='PEM'))
        return

    def Transfer(self, sender, recipient, value):
        sender.Credits = self.AccountGet(sender)
        recipient.Credits = self.AccountGet(recipient)
        if sender.Credits > value:
           sender.Credits -= value
           recipient.Credits += value
           #self.time = datetime.datetime.now()
           self.timestamp = int(time.time())
           print('Transaction finished at %s' % (self.timestamp))
        self.AccountSave(sender)
        self.AccountSave(recipient)

        tranDetailStr = "sender:%s,recipient:%s,value:%.8f,timestamp:%s" % (sender.Name,recipient.Name,value,self.timestamp)
        signStr = self.SignTransaction(tranDetailStr)
        str1 = "%s,signstr:%s,pubkey:%s" % (tranDetailStr,signStr,self._public_key_str.decode('utf-8'))
        self.TransactionSave(str1)
        return 

    def AccountGet(self, Stu): #存储账户余额信息
        cred = Stu.Credits
        config = configparser.ConfigParser()
        config.read(self.iniFileName, encoding='utf-8')
        list = config.sections()    # 获取到配置文件中所有分组名称
        if Stu.Name in list: # 如果分组存在
            cred = config.getfloat(Stu.Name, "Credits")
        return cred

    def TransactionSave(self, tranStr): #存储交易信息
        txtFileName = 'TranscationLists.txt'
        f = open(txtFileName, "a+")
        f.write(tranStr)
        f.close()
        return

    def AccountSave(self, Stu): #存储账户余额信息
        config = configparser.ConfigParser()
        config.read(self.iniFileName, encoding='utf-8')
        list = config.sections()    # 获取到配置文件中所有分组名称
        if Stu.Name not in list: # 如果分组不存在
            config.add_section(Stu.Name)   # 增加section
        config.set(Stu.Name,"Credits",str(Stu.Credits))
        with open(self.iniFileName, "w+") as f:
            config.write(f)
            f.close()
        return

    def SignTransaction(self,tranStr=''): #返回签名后的字符串, tranStr为源字符串、没有经过hash处理
        signer = PKCS1_v1_5.new(self._private_key)
        h = Crypto.Hash.SHA256.new(tranStr.encode('utf-8'))
        hStr = h.hexdigest()
        str2 = signer.sign(h)
        str3 = base64.b32encode(str2).decode('utf-8')
        return str3

    def VerifyTransaction(self):
        txtFileName = 'TranscationLists.txt'
        f = open(txtFileName, "r")
        tranStr = f.read()
        f.close()
        strs = tranStr.split('\n\n')
        rstValue = False
        for str in strs:
            if len(str)>0:
                rstValue = False
                list1 = str.split(',')
                sender = list1[0].split(":")[1]
                recipient = list1[1].split(":")[1]
                valueStr = list1[2].split(":")[1]
                timestampStr  = list1[3].split(":")[1]
                signStr= list1[4].split(":")[1]
                pubkey= list1[5].split(":")[1]
                tranDetailStr = "sender:%s,recipient:%s,value:%s,timestamp:%s" % (sender,recipient,valueStr,timestampStr)
                print(str)

                pubkeyPem = base64.b32decode(pubkey)
                keyPub = Crypto.PublicKey.RSA.importKey(pubkeyPem)
                verifer = Crypto.Signature.PKCS1_v1_5.new(keyPub)
                msg_hash = Crypto.Hash.SHA256.new()
                msg_hash.update(tranDetailStr.encode('utf-8'))
                hStr1 = msg_hash.hexdigest()
                rstValue = verifer.verify(msg_hash, base64.b32decode(signStr)) # 使用公钥验证签名

        return rstValue
    

StuA = Student('A')
StuB = Student('B')
tran = Transaction(StuA)    # StuA发起的交易
tran.Transfer(StuA,StuB,10)
tranB =Transaction(StuB) 
print(tranB.VerifyTransaction())


#print('Student: %s has %f credits' % (StuA.Name,StuA.Credits))
#print('Student: %s has %f credits' % (StuB.Name,StuB.Credits))