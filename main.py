import datetime


class Student:
    Name = ""
    Credits = 20.0

    def __init__(self, name=""):
        self.Name = name


class Transaction:
    def __init__(self, sender, recipient, value):
        if sender.Credits > value:
            sender.Credits -= value
            recipient.Credits += value
            self.time = datetime.datetime.now()
            print("Transaction finished at %s" % (self.time))


def main():
    StuA = Student("A")
    StuB = Student("B")
    tran = Transaction(StuA, StuB, 10)

    print("Student: %s has %f credits" % (StuA.Name, StuA.Credits))
    print("Student: %s has %f credits" % (StuB.Name, StuB.Credits))


if __name__ == "__main__":
    main()
