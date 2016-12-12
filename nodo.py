import socket
import pickle
import threading
import os
import sys
import commands
import time

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
        #creacion carperta compartida
        commands.getoutput('rm -r Compartida/ | mkdir Compartida')
        commands.getoutput('mkdir Compartida')

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
                        print '<%s> %s' %(user,data)
                    except:
                        break
                print '<%s> desconectado' % user
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

    def cargar_archivo(self,path):
        #creacion de archivo
        nuevo=open(path,'wb')
        print 'archivo creado'
        #escritura de archivo
        ch=self.soc_serv_central.recv(8192)
        while ch != 'EOF':
            #print len(ch)
            nuevo.write(ch)
            ch=self.soc_serv_central.recv(8192)
        #cierre de archivo
        print 'cerrando arch'
        nuevo.close()

    def funcion_servidor_central(self):
        while 1:
            try:
                #print 'Esperando SC: '
                datos=pickle.loads(self.soc_serv_central.recv(1028))
                print 'Recibido de SC: ',datos[0]
                if datos[0]=='new':
                    self.conectar_nodo(datos[1])
                elif datos[0]=='drop':
                    #print '<%s> desconectando',datos[1]
                    self.borrar_nodo(datos[1])
                elif datos[0]=='update':
                    self.cargar_archivo('Compartida/'+datos[1])
            except:
                break
        return

    def enviar_archivo(self,data):
        print 'subiendo archivo ...'
        try:
            #verificar si el path es correcto
            arch=open(data[1],'rb')
        except Exception as e:
            print 'Error',e
        else:
            self.soc_serv_central.send(pickle.dumps((data[0],data[1].split('/')[-1])))
            time.sleep(0.01)
            bytes_read = arch.read(8192)
            while bytes_read:
                #print len(bytes_read)
                time.sleep(0.0001)
                self.soc_serv_central.send(bytes_read)
                bytes_read = arch.read(8192)
            print 'send end'
            time.sleep(0.1)
            self.soc_serv_central.send('EOF')
            arch.close()

    def funcion_prompt(self):
        while 1:
            data=raw_input().split()
            if data:
                if data[0]=='upload':
                    #comando para copiar archivo a la carpeta
                    #---
                    #pilas con el demonio, debe hacer esto:
                    self.enviar_archivo(data)
                else:
                    print '<%s> %s' %(self.nombre_usuario,' '.join(data))
                    for s in self.nodos:
                        s.send(pickle.dumps(' '.join(data)))


    def iniciar_servidor(self):
        threading.Thread(target=self.funcion_servidor).start()

    def escuchar_servidor_central(self):
        threading.Thread(target=self.funcion_servidor_central).start()

    def iniciar_prompt(self):
        threading.Thread(target=self.funcion_prompt).start()

exp=Nodo(int(sys.argv[1]),'localhost',1038)
