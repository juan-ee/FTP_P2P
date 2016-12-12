import threading
import socket
import pickle
import os
import time

class Hilo(threading.Thread):
    def __init__(self,nombre,soc,args=()):
        self.nombre=nombre
        self.soc=soc
        self.args=args
        threading.Thread.__init__(self)
        return

    def borrar_nodo(self):
        #removiendo el hilo de ejecucion
        self.args[0].remove(threading.currentThread())
        #enviando alerta de desconexion a cada nodo
        for h in self.args[0]:
            h.soc.send(pickle.dumps(('drop',self.args[1][self.nombre])))
        #borrando el registro del nodo
        del self.args[1][self.nombre]
        self.soc.close()
        print '<%s> se ha desconectado' % self.nombre

    def informar_nuevo(self,host,puerto):
        self.soc.send(pickle.dumps(('new',(host,puerto))))

    def cargar_archivo(self,path):
        #creacion de archivo
        nuevo=open(path,'wb')
        print 'archivo creado'
        #escritura de archivo
        ch=self.soc.recv(8192)
        while ch != 'EOF':
            #print len(ch)
            nuevo.write(ch)
            ch=self.soc.recv(8192)
        #cierre de archivo
        print 'cerrando arch'
        nuevo.close()

    def enviar_archivo(self,data):
        print 'subiendo archivo ...'
        try:
            arch=open(path,'rb')
        except Exception as e:
            print 'Error',e
        else:
            self.soc.send(pickle.dumps(('update',path.split('/')[-1])))
            time.sleep(0.01)
            chunk = arch.read(8192)
            while chunk:
                time.sleep(0.0001)
                self.soc_serv_central.send(chunk)
                chunk = arch.read(8192)
            time.sleep(0.1)
            self.soc_serv_central.send('EOF')
            arch.close()

    def replicar_nodos(self,path):
        for h in argv[0]:
            if h!=threading.currentThread():
                h.enviar_archivo(path)


    def run(self):
        while 1:
            print 'otro loop'
            try:
                data = pickle.loads(self.soc.recv(1024))
                print data
                if data[0] == 'upload':
                    path='Compartida/'+data[1]
                    self.cargar_archivo(path)
                    self.replicar_nodos(path)

                else:
                    print data
            except Exception as e:#Desconexion inesperada
                print e
                self.borrar_nodo()
                break
        print 'Se acabo el while'
        return
