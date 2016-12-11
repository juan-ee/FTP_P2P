import socket
import pickle
import os
from hilo import Hilo


def verificar_usuario(us,nodos,client):

    while 1:
        if us[0] in nodos:
            client.send('fail')
        else:
            client.send('accepted')
            break
        try:
            #aqui puede haber un error por el tamano del buffer leido
            us=pickle.loads(client.recv(1028))
        except Exception as e:
            print 'Error: ',e
    return us

print 'iniciando servidor ...'
host = ''
port = 1034
backlog = 5
size = 1024
nodos={}
hilos=[]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)

while 1:
    client, address = s.accept()

    try:
    #us sera el nombre del usuario que se usara en la red P2P
        us=verificar_usuario(pickle.loads(client.recv(size)),nodos,client)
    except:
        continue

    #enviar lista de conectados
    client.send(pickle.dumps(nodos))

    #enviar a cada nodo el nuevo cliente conectado
    print 'Informando a: ', hilos
    for h in hilos:
        h.informar_nuevo(address[0],us[1])

    #agregar el nuevo nodo al diccionario
    nodos[us[0]]=(address[0],us[1])

    #agregar hilo de ejecucion
    hilos.append(Hilo(us[0],client,args=(hilos,nodos,)))
    hilos[-1].start()

    #enviar_nuevo_nodo(nodos,address[0],us[1])
