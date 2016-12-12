import sys
import time
import pyinotify
import daemon 
import os.path

archivo = open("eventos.log", "a")

def log(text):
	archivo.write(text + "\n")
	archivo.flush()

class EventHandler(pyinotify.ProcessEvent):
		
	def process_IN_CREATE(self, event):
    		if os.path.basename(event.pathname)[0] != '.':
        		print "Creado:", event.name

	def process_IN_DELETE(self, event):
		archive = os.path.basename(event.pathname)
		if os.path.basename(event.pathname)[0] != '.':	
			print "Borrado:", event.name
	
	def process_IN_MODIFY(self, event):
		if os.path.basename(event.pathname)[0] != '.':
			print "Modicado:", event.name

	def process_IN_MOVED_FROM(self,event):
    		if os.path.basename(event.pathname)[0] != '.':
			print 'Movido afuera carpeta:', event.name

	def process_IN_MOVED_TO(self,event):
    		if os.path.basename(event.pathname)[0] != '.':
			print 'Movido a la de la carpeta:', event.name


	
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, EventHandler())

wm.add_watch(sys.argv[1],pyinotify.IN_MODIFY | pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO)

notifier.loop()


