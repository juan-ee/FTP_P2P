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
        self.dir='Compartida'
        self.buff=2048
        self.iniciar_servidor()
        self.nodos=[]
        self.conectar_red(host_sc,puerto_sc)
        self.iniciar_prompt()
        self.bandera=True

    def conectar_red(self,host,puerto):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,puerto))

        while 1:
            nombre_usuario=raw_input('Escriba un nombre de usuario: ')
            if not nombre_usuario:
                print 'Nombre incorrecto'
            else:
                s.send(pickle.dumps((nombre_usuario,self.puerto)))
                if s.recv(self.buff)=='fail':
                    print 'Nombre de usuario ya existente'
                else:
                    break
        print 'Hola %s! Bienvenido a la red P2P' % nombre_usuario
        #nombre de usuario
        self.nombre_usuario=nombre_usuario
        #conexion a los demas nodos
        self.soc_serv_central=s
        #carpeta compartida
        commands.getoutput('rm -r '+self.dir+'/')
        commands.getoutput('mkdir '+self.dir)
        #servidor central
        self.escuchar_servidor_central()
        #creacion carperta compartida

    def conectar_nodo(self,nodo):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(nodo)
        s.send(pickle.dumps(self.nombre_usuario))
        self.nodos.append(s)


    def funcion_servidor(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('',self.puerto))
        s.listen(5)

        while 1:
            client, address = s.accept()
            #nombre de usuario
            user=pickle.loads(client.recv(self.buff))
            print '<%s> conectado' %user

            if os.fork()==0:
                while 1:
                    try:
                        datos = pickle.loads(client.recv(self.buff))
                        print datos
                        if datos[0]=='upload':
                            #if self.bandera:
                            #self.enviar_a_todos(('off'))
                            h=threading.Thread(target=self.cargar_archivo,args=(''+self.dir+'/'+datos[1],))
                            h.start()
                            h.join()
                            #self.cargar_archivo(''+self.dir+'/'+datos[1])
                            #self.enviar_a_todos(('on'))
                        elif datos[0]=='remove':
                            print 'borrando..'
                            #self.enviar_a_todos(('off'))
                            print commands.getoutput('rm '+self.dir+'/'+datos[1])
                            #self.enviar_a_todos(('on'))
                        elif datos[0] == 'message':
                            print '<%s> %s' %(user,datos[1])

                        elif datos[0]=='off':
                            print 'apagando bandera'
                            self.bandera=False

                        elif datos[0]=='on':
                            print 'encendiendo bandera'
                            self.bandera=True

                    except Exception as e:
                        print 'Error server leyendo:',e
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
        with open(path,'wb') as nuevo:
            print path,'creado'
            #escritura de archivo
            ch=self.soc_serv_central.recv(self.buff)
            while ch!='EOF':
                #print len(ch)
                nuevo.write(ch)
                ch=self.soc_serv_central.recv(self.buff)
            print 'cerrando arch'
            return

    def funcion_servidor_central(self):
        while 1:
            try:
                datos=pickle.loads(self.soc_serv_central.recv(self.buff))
                print 'Recibido de SC: ',datos[0]
                if datos[0]=='new':
                    self.conectar_nodo(datos[1])
                elif datos[0]=='drop':
                    self.borrar_nodo(datos[1])
                elif datos[0]=='load_dir':
                    for f in datos[1]:
                        h=threading.Thread(target=self.cargar_archivo,args=(''+self.dir+'/'+f,))
                        h.start()
                        h.join()
                elif datos[0]=='join':
                    for n in datos[1]:
                        self.conectar_nodo((datos[1][n][0],datos[1][n][1]))
            except Exception as e:
                print 'Error con SC: ',e
        print 'se acabo el while'
        return

    def enviar_archivo(self,soc,path):
        print 'subiendo archivo ...'
        #self.soc.send(pickle.dumps(('update',path.split('/')[-1])))
        with open(path,'rb') as f:
            for chunk in iter((lambda:f.read(self.buff)),''):
                time.sleep(0.01)
                #print len(chunk)
                soc.send(chunk)
            time.sleep(0.1)
            soc.send('EOF')

    def enviar_archivo_a_todos(self,data):
        self.soc_serv_central.send(pickle.dumps((data[0],data[1].split('/')[-1])))
	time.sleep(0.1)
        self.enviar_archivo(self.soc_serv_central,data[1])
        for s in self.nodos:
            s.send(pickle.dumps((data[0],data[1].split('/')[-1])))
            time.sleep(0.1)
            self.enviar_archivo(s,data[1])

    def enviar_a_todos(self,data):
        for s in self.nodos:
            s.send(pickle.dumps(data))

    def funcion_prompt(self):
        while 1:
            data=raw_input().split()
            if data:
                if data[0]=='upload':
                    #comando para copiar archivo a la carpeta
                    if commands.getstatusoutput('cp '+data[1]+' ./'+self.dir+'/')[0] != 0:
                        print 'Path incorrecto'
                elif data[0]=='remove':
                    if data[1] in commands.getoutput('ls '+self.dir+'/').split():
                        commands.getoutput('rm '+self.dir+'/'+data[1])
                        #self.enviar_a_todos((data[0],data[1]))
                        #self.soc_serv_central.send(pickle.dumps((data[0],data[1])))
                    else:
                        print 'Archivo no existente'
                elif data[0]=='list':
                    print commands.getoutput('ls -l '+self.dir+'/')
                else:
                    print '<%s> %s' %(self.nombre_usuario,' '.join(data))
                    self.enviar_a_todos(('message',' '.join(data)))


    def iniciar_servidor(self):
        threading.Thread(target=self.funcion_servidor).start()

    def escuchar_servidor_central(self):
        threading.Thread(target=self.funcion_servidor_central).start()

    def iniciar_prompt(self):
        threading.Thread(target=self.funcion_prompt).start()
