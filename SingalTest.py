
from PyQt5.QtCore import *

class MySignal(QObject):
    sendmsg = pyqtSignal(object)

    def run(self):
        self.sendmsg.emit('HEllo!!')

class getMsg(QObject):
    def get(self,msg):
        print("Hello"+msg)

if __name__ == '__main__':
    send = MySignal()
    slot = getMsg ()
    send.sendmsg.connect(slot.get)
    send.run()