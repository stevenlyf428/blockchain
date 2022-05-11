class Student:
    Name = ''
    Credits = 20.0
    def __init__(self,name=''):
        self.Name = name


StuA = Student('A')
print('Student: %s has %f credits' % (StuA.Name,StuA.Credits))
StuB = Student('B')
print('Student: %s has %f credits' % (StuB.Name,StuB.Credits))
