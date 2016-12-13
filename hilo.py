import threading
import socket
import pickle
import os
import time
import commands

class Hilo(threading.Thread):
    def __init__(self,nombre,soc,args=()):
        self.buff=2048
        self.nombre=nombre
        self.soc=soc
        self.args=args
        self.enviar_carpeta()
        self.conectar_nodos()
        threading.Thread.__init__(self)
        return

    def conectar_nodos(self):
        #enviar lista de conectados
        print 'enviando lista:',self.args[1]
        self.soc.send(pickle.dumps(('join',self.args[1])))

    def enviar_carpeta(self):
        ls=commands.getoutput('ls Compartida/').split()
        if ls:
            self.soc.send(pickle.dumps(('load_dir',ls)))
            for f in ls:
                print 'enviando',f
                self.enviar_archivo('Compartida/'+f)


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
        ch=self.soc.recv(self.buff)
        while ch != 'EOF':
            #print len(ch)
            nuevo.write(ch)
            ch=self.soc.recv(self.buff)
        #cierre de archivo
        print 'cerrando arch'
        nuevo.close()

    def enviar_archivo(self,path):
        try:
            arch=open(path,'rb')
        except Exception as e:
            print 'Error',e
        else:
            self.soc.send(pickle.dumps(('update',path.split('/')[-1])))
            time.sleep(0.01)
            chunk = arch.read(self.buff)
            while chunk:
                time.sleep(0.0001)
                self.soc.send(chunk)
                chunk = arch.read(self.buff)
            time.sleep(0.1)
            self.soc.send('EOF')
            arch.close()

    def run(self):
        while 1:
            print 'otro loop'
            try:
                data = pickle.loads(self.soc.recv(self.buff))
                print data
                if data[0] == 'upload':
                    path='Compartida/'+data[1]
                    self.cargar_archivo(path)
                    #self.replicar_nodos(path)
                elif data[0] == 'remove':
                    print 'borrando..'
                    commands.getoutput('rm Compartida/'+data[1])
                    #self.informar_borrado(data[1])
                else:
                    print data
            except Exception as e:#Desconexion inesperada
                print e
                self.borrar_nodo()
                break
        print 'Se acabo el while'
        return

"""
    def replicar_nodos(self,path):
        for h in self.args[0]:
            if h!=threading.currentThread():
                h.enviar_archivo(path)

    def informar_borrado(self,arch):
        for h in self.args[0]:
            if h!=threading.currentThread():
                h.soc.send(pickle.dumps(('remove',arch)))
"""
