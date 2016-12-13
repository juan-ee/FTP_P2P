import sys
import time
import pyinotify
import daemon
import pickle
import os.path
from nodo import Nodo

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self,nodo):
        self.obj=nodo
        pyinotify.ProcessEvent.__init__(self)

    def process_IN_CREATE(self, event):
        if os.path.basename(event.pathname)[0] != '.':
            print 'upload',event.name
            time.sleep(0.1)
            self.obj.enviar_archivo(('upload',self.obj.dir+'/'+event.name))

    def process_IN_DELETE(self, event):
        if os.path.basename(event.pathname)[0] != '.':
            print 'remove',event.name
            self.obj.soc_serv_central.send(pickle.dumps(('remove',event.name)))

    def process_IN_MODIFY(self, event):
        if os.path.basename(event.pathname)[0] != '.':
            print 'upload',event.name
            time.sleep(0.1)
            self.obj.enviar_archivo(('upload',self.obj.dir+'/'+event.name))

    def process_IN_MOVED_FROM(self,event):
        if os.path.basename(event.pathname)[0] != '.':
            print 'remove',event.name
            self.obj.soc_serv_central.send(pickle.dumps(('remove',event.name)))

    def process_IN_MOVED_TO(self,event):
        if os.path.basename(event.pathname)[0] != '.':
            print 'upload',event.name
            time.sleep(0.1)
            self.obj.enviar_archivo(('upload',self.obj.dir+'/'+event.name))

wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, EventHandler(Nodo(int(sys.argv[1]),'localhost',1039)))
wm.add_watch('Compartida',pyinotify.IN_MODIFY | pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO)
notifier.loop()
