import threading
import socket
import pickle

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

    def run(self):
        while 1:
            try:
                data = pickle.loads(self.soc.recv(16))
                if data == 'close()':
                    self.borrar_nodo()
                    break
                else:
                    print data
            except Exception as e:#Desconexion inesperada
                print e
                self.borrar_nodo()
                break
        return
