import socket
import pickle
import threading
import os
import sys

class Nodo(object):

    def __init__(self,puerto,host_sc,puerto_sc):
        self.puerto=puerto
        self.iniciar_servidor()
        self.nodos=[]
        self.conectar_red(host_sc,puerto_sc)
        self.iniciar_prompt()

    def conectar_red(self,host,puerto):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,puerto))

        while 1:
            nombre_usuario=raw_input('Escriba un nombre de usuario: ')
            if not nombre_usuario:
                print 'Nombre incorrecto'
            else:
                s.send(pickle.dumps((nombre_usuario,self.puerto)))
                if s.recv(8)=='fail':
                    print 'Nombre de usuario ya existente'
                else:
                    break
        print 'Hola %s! Bienvenido a la red P2P' % nombre_usuario
        self.nombre_usuario=nombre_usuario
        self.conectar_nodos(pickle.loads(s.recv(1028)))
        self.soc_serv_central=s
        self.escuchar_servidor_central()

    def conectar_nodos(self,nodos):
        for n in nodos:
            self.conectar_nodo((nodos[n][0],nodos[n][1]))

    def conectar_nodo(self,nodo):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(nodo)
        s.send(pickle.dumps(self.nombre_usuario))
        self.nodos.append(s)


    def funcion_servidor(self):
        #print 'iniciando servidor ...'
        """
        size = 1024
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('',self.puerto))
        s.listen(5)
        """
        size = 1024
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('',self.puerto))
        s.listen(5)

        while 1:
            client, address = s.accept()
            #nombre de usuario
            user=pickle.loads(client.recv(size))

            print '<%s> conectado' %user

            if os.fork()==0:
                while 1:
                    try:
                        data = pickle.loads(client.recv(size))
                        print client
                        if data != 'close()':
                            print '<%s> %s' %(user,data)
                        else:
                            print '<%s> se ha desconectado' % user
                            break
                    except:
                        break
                client.close()
            else:
                client.close()
        return

    def borrar_nodo(self,nodo):
        for n in self.nodos:
            if n.getpeername() == nodo:
                n.close()
                self.nodos.remove(n)
                break

    def funcion_servidor_central(self):
        while 1:
            try:
                print 'Esperando SC: '
                datos=pickle.loads(self.soc_serv_central.recv(1028))
                print 'Recibido de SC: ',datos[0]
                if datos[0]=='new':
                    self.conectar_nodo(datos[1])
                elif datos[0]=='drop':
                    print 'desconectando',datos[1]
                    self.borrar_nodo(datos[1])



            except Exception as e:
                print 'Error',e
                break
        return

    def funcion_prompt(self):
        while 1:
        	data=raw_input()
                #print self.nodos
                print '<%s> %s' %(self.nombre_usuario,data)
                for s in self.nodos:
                    print s
                    s.send(pickle.dumps(data))
            	if data=='close()':
            		break

    def iniciar_servidor(self):
        threading.Thread(target=self.funcion_servidor).start()

    def escuchar_servidor_central(self):
        threading.Thread(target=self.funcion_servidor_central).start()

    def iniciar_prompt(self):
        threading.Thread(target=self.funcion_prompt).start()

exp=Nodo(int(sys.argv[1]),'localhost',1034)
