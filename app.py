import sys
import time
import pyinotify
#import daemon
import pickle
import os.path
from nodo import Nodo

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self,nodo):
        self.obj=nodo
        pyinotify.ProcessEvent.__init__(self)

    def process_IN_CREATE(self, event):
        if os.path.basename(event.pathname)[0] != '.' and os.path.basename(event.pathname)[-1] != '~':
            print 'created',self.obj.nombre_usuario,self.obj.bandera
            time.sleep(1)
            if self.obj.bandera:
                print 'created-bandera true'
                self.obj.enviar_a_todos(('off',0))
                self.obj.enviar_archivo_a_todos(('upload',self.obj.dir+'/'+event.name))
                self.obj.enviar_a_todos(('on',1))
            else:
                print 'created-bandera false'

    def process_IN_DELETE(self, event):
        if os.path.basename(event.pathname)[0] != '.' and os.path.basename(event.pathname)[-1] != '~':
            #print 'remove',event.name
            if self.obj.bandera:
                print 'delete-bandera true'
                self.obj.enviar_a_todos(('off',0))
                self.obj.soc_serv_central.send(pickle.dumps(('remove',event.name)))
                self.obj.enviar_a_todos(('remove',event.name))
                self.obj.enviar_a_todos(('on',1))
            else:
                print 'delete-bandera false'

    def process_IN_MOVED_FROM(self,event):
        if os.path.basename(event.pathname)[0] != '.':
            if self.obj.bandera:
                print 'delete-bandera true'
                self.obj.enviar_a_todos(('off',0))
                self.obj.soc_serv_central.send(pickle.dumps(('remove',event.name)))
                self.obj.enviar_a_todos(('remove',event.name))
                self.obj.enviar_a_todos(('on',1))
            else:
                print 'delete-bandera false'

    def process_IN_MOVED_TO(self,event):
        if os.path.basename(event.pathname)[0] != '.':
            print 'moved to',self.obj.nombre_usuario,self.obj.bandera
            time.sleep(1)
            if self.obj.bandera:
                print 'created-bandera true'
                self.obj.enviar_a_todos(('off',0))
                self.obj.enviar_archivo_a_todos(('upload',self.obj.dir+'/'+event.name))
                self.obj.enviar_a_todos(('on',1))
            else:
                print 'created-bandera false'

wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, EventHandler(Nodo(int(sys.argv[1]),'localhost',1040)))
time.sleep(5)
wm.add_watch('Compartida',pyinotify.IN_MODIFY | pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO)
notifier.loop()


"""    def process_IN_MODIFY(self, event):
        if os.path.basename(event.pathname)[0] != '.':
            print 'upload',event.name
            time.sleep(0.1)
            self.obj.enviar_archivo(('upload',self.obj.dir+'/'+event.name))
"""
