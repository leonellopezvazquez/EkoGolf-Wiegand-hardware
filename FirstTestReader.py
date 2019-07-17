#!/usr/bin/python -u
import time, sys, readline, re, getopt, os
import select
import traceback
import commands
import saturn
import string
import binascii
import threading
import signal
import socket
import atexit
import serial

from socket import *
import socket as SocketServer


class JQ_Event:
    def __init__(self,host='localhost',port=50008,timeout=None):
        if (host != 'localhost'):
            self.HOST = host
            self.PORT = port 
			
            self.clientsocket = socket(AF_INET, SOCK_STREAM)
            self.clientsocket.connect((self.HOST, self.PORT))
        else:
            self.clientsocket = socket(AF_UNIX, SOCK_STREAM)
            self.clientsocket.connect('/tmp/50008')

        self.id = (self.clientsocket.recv(512).split('=')[1]).strip()
        self.clientsocket.settimeout(timeout)

    def getid(self):
        return self.id

    def settimeout(self,timeout):
        self.clientsocket.settimeout(timeout)

    def receive(self,function):  
        data = ''
        while 1:
            try:
                data += self.clientsocket.recv(1024)
                if data.find("\r\n\r\n") != -1:
                    term_pos = data.rfind("\r\n\r\n") + 4
                    data_aux = data[:term_pos].strip()
                    data = data[term_pos:]
                    function(data_aux)
            except:
                print("Evento incorrecto")
        
    def close(self):
        self.clientsocket.close()



VERSION="TEO CU 2018.02 -  v 1.0.1"
HOST = 'localhost' # The remote host
COMMAND_PORT = 50007
EVENT_PORT   = 50008

####Serial settings
SERIAL_PORT=0
BAUDRATE=9600
rtscts=0
xonxoff=0
tx_sequence=0
sport = None
bcc_mode = False
serial_out=True


debug=True
eot_mode=0
demo_out=''
CR='\x0D'
LF='\x0A'
CRLF='\x0D\x0A'
ESC='\x1B'
BL_ON='B1'    # blank on
BL_OFF='B0'   # blank off
FL_ON='F1'    # flash on
FL_OFF='F0'   # flash off
EOT=CR


#TCP IP Server
HOST_SERVER = "169.254.1.1"
sMUX ="OFF-OFF-OFF-OFF-"
ANTENNA1 = "OFF"
ANTENNA2 = "OFF"
ANTENNA3 = "OFF"
ANTENNA4 = "OFF"

ATTENUATION1 = "0"
ATTENUATION2 = "0"
ATTENUATION3 = "0"
ATTENUATION4 = "0"


TAGS_PORT = 50010
IsClientConnected = False
conn = None
addr = None
StopApp = False


try:
	print "Iniciando "
	if sys.argv[1] != None:
		HOST_SERVER = sys.argv[1]
	if sys.argv[2] != None:
		sMUX = sys.argv[2]
		
	la_antenas = sMUX.split("-")
	if la_antenas[0] =="ON":
		ANTENNA1 = "ON"
	if la_antenas[1] =="ON":
		ANTENNA2 = "ON"
	if la_antenas[2] =="ON":
		ANTENNA3 = "ON"
	if la_antenas[3] =="ON":
		ANTENNA4 = "ON"
			
	if sys.argv[3] != None:
		ATTENUATION1 = sys.argv[3]
	if sys.argv[4] != None:
		ATTENUATION2 = sys.argv[4]
	if sys.argv[5] != None:
		ATTENUATION3 = sys.argv[5]
	if sys.argv[6] != None:
		ATTENUATION4 = sys.argv[6]
		
	 
except getopt.GetoptError:
    sys.exit(2)

def WiegandCode(user_data):

	firstsplitt=user_data[:30]

	wiegandCode = firstsplitt[22:]

	fc = wiegandCode[:4]

	cc = wiegandCode[4:]
	

	fc = str(fc)
	cc =str(cc)

	strfc = str(int(fc,16))
	strcc = str(int(cc,16))

	if int(fc,16) == 0 or int(cc,16) == 0:
		return "0"
	
	StrFc = ""
	StrCc = ""


    ####Fc

	if len(strfc) == 1:
		StrFc="00"+strfc

	if len(strfc) == 2:
		StrFc="0"+strfc

	if len(strfc) == 3:
		StrFc=strfc

    #####CC

	if len(strcc) == 1:
		StrCc="0000"+strcc

	if len(strcc) == 2:
		StrCc="000"+strcc

	if len(strcc) == 3:
		StrCc="00"+strcc

	if len(strcc) == 4:
		StrCc="0"+strcc

	if len(strcc) == 5:
		StrCc = strcc

	return StrFc+StrCc


def send_serial(response, sequence):
	RES =""
	try:
		STX=''
		
 
		if response=="":
			return
		
		else:
			res = str(response)
			RES=""
			RES = WiegandCode(res)

			if RES == "0":
				return
			
			response = STX + response 

			if bcc_mode:
		# calculate block check (xor of data)
				bcc = 0
				for i in response:
					bcc ^= ord(i)
			
				response = response + EOT + str("%02x" % bcc)

				if debug:
					print "bcc of response %02x" % bcc 

			else:     
				response += EOT 

			if debug:
				print "sending response %s" % response 
		
			#####wiegand part


			#response = "#" + response + CRLF

			
			print "sending response %s" % RES 
			
			for char in RES:
				print char
				sport.write(char)
	
		response = ""

	except:   
		traceback.print_exc(file=sys.stdout)   


# callback to handle tag arrive events
def tag_event(event):
	try:
		t = threading.Thread(target=HiloProcesaEventoTags, kwargs={'eventos': event })
		t.start()
	except:
		print("No se logro iniciar el hilo para procesar el Tag")



def HiloProcesaEventoTags(**datos):
	global conn
	global IsClientConnected
	
	la_events = datos['eventos'].split("\r\n\r\n")
	for lc_event in la_events:
		if lc_event == "":
			continue
		else:
			tag_id = "NULL"
			tid = "NULL"
			user = "NULL"
			lc_tagtype = "ISOC"
			nAntenna =0

			elist = lc_event.split()	
			#print(elist)		
			for a in elist:
				if (a.find("tag_id=") >= 0):
					tag_id = (a.strip(',')).replace("tag_id=0x","",1)
				if (a.find("tid=0x") >= 0):
					tid = (a.strip(',')).replace("tid=0x","",1)
					tid = tid[:24]
				if (a.find("type=") >= 0):
					lc_tagtype = (a.strip(',')).replace("type=","",1)
				if (a.find("antenna") >= 0):
					nAntenna = (a.strip(',')).replace("antenna=","",1)
				if (a.find("user_data")>=0):
					user = (a.strip(',')).replace("user_data=","",1)

			if lc_tagtype != "ISOC":
				return
			
			if tag_id == "NULL" or tag_id =="" or user == "NULL":
				return
				
			if len(tid) > 24:
				tid = tid[:24]
		
			
			try:
				#print(tag_id +"|"+tid+"|"+"|"+nAntenna+"|"+user)
				send_serial(user, "")
				#conn.send((tag_id +"|"+tid+"|"+nAntenna+"\n").encode())
			except:
				print "Se ha perdido la conexion con el cliente"


# main callback for all events
def event_receiver(event):
    event_handlers.get(event[:9], unknown_event)(event)

# list of events and their callbacks
event_handlers = {
    'event.tag': tag_event,
}

# callback for unknown events
def unknown_event(event):
    print "unknown event: %s" % event


# signal handler for termination
def sig_handler(signum, frame):
	print ("Termina aplicacion")
	StopApp = True	
	IsClientConnected = False
	conn.close()
	##mySocket.shutdown(1)
	##mySocket.close()
	cmd.close()
	evt.close()
	sys.close()


def Running():
	print "running"
	while 1:
		time.sleep(100)
		print "running"


try:
	print "starting"

	
	signal.signal(signal.SIGTERM, sig_handler)
	timer_running = 0
	#open the command channel
	cmd = saturn.Command(HOST,COMMAND_PORT)
	#open the event channel
	evt = JQ_Event(HOST,EVENT_PORT)
	#obtain the event channel id	
	evtid = evt.getid()
	


	# register for tag report events
	#cmd.sendcommand('reader.events.register(id='+evtid+',name=event.tag.report)')
	#cmd.sendcommand('tag.reporting.report_fields = tag_id tid type prot_data antenna')

    ###### activate Serial Port
    ###### disable CLI from Serial
    #disable CLI

	
	print "Saturn OK"

	"""
	try:
		rc = cmd.sendcommand('com.serial.console(program=none)')
		if rc[0] != "ok":
			print("error setting console to none: %s " % rc[0])

		sport = serial.Serial(SERIAL_PORT, BAUDRATE, rtscts=rtscts, xonxoff=xonxoff)
		print("Openning serial port at %s ..." % BAUDRATE)
    
	except e:
		print(e)
		sys.stderr.write("Could not open port\n")
		sys.exit(1)

	"""


	try:
		rc = cmd.sendcommand('com.serial.console(program=none)')
		if rc[0] != "ok":
			print("error setting console to none: %s " % rc[0])
			
		sport = serial.Serial(SERIAL_PORT, BAUDRATE, rtscts=rtscts, xonxoff=xonxoff)
		print("Openning serial port at %s ..." % BAUDRATE)

	except:
		print "Error Disable CLI"

	
	cmd.sendcommand('reader.events.register(id='+evtid+',name=event.tag.arrive)')
	cmd.sendcommand('tag.reporting.arrive_fields = tag_id tid type prot_data antenna user_data')
	
	AntennasEnable =""
	if ANTENNA1 =="ON":
		AntennasEnable = "1"
	if ANTENNA2 =="ON":	
		AntennasEnable += " 2"
	if ANTENNA3 =="ON":	
		AntennasEnable += " 3"
	if ANTENNA4 =="ON":	
		AntennasEnable += " 4"
		
	cmd.sendcommand('antennas.set(configuration=all_monostatic, mux_sequence= '+AntennasEnable+')')
	
	if ANTENNA1 =="ON":
		cmd.sendcommand('antennas.1.set(conducted_power=0)')
		cmd.sendcommand('antennas.1.advanced.set(attenuation='+ATTENUATION1+', cable_loss=18, gain=130, gain_units=dbi)')
	if ANTENNA2 =="ON":	
		cmd.sendcommand('antennas.2.set(conducted_power=0)')
		cmd.sendcommand('antennas.2.advanced.set(attenuation='+ATTENUATION2+', cable_loss=18, gain=130, gain_units=dbi)')
	if ANTENNA3 =="ON":	
		cmd.sendcommand('antennas.3.set(conducted_power=0)')
		cmd.sendcommand('antennas.3.advanced.set(attenuation='+ATTENUATION3+', cable_loss=18, gain=130, gain_units=dbi)')
	if ANTENNA4 =="ON":	
		cmd.sendcommand('antennas.4.set(conducted_power=0)')
		cmd.sendcommand('antennas.4.advanced.set(attenuation='+ATTENUATION4+', cable_loss=18, gain=130, gain_units=dbi)')
	 
	cmd.sendcommand('modem.protocol.isoc.control.user_data_length = 10')

	rc = cmd.sendcommand('setup.operating_mode=active')
	# print out the startup parameters
	print "Program %s - Version: %s" % (sys.argv[0], VERSION)
	
	#w = threading.Thread(target=Running)
	#w.start()
	evt.receive(event_receiver)	
	
except:
	print("Error")
	traceback.print_exc(file=sys.stdout)
	cmd.sendcommand('setup.operating_mode = standby')
	cmd.sendcommand('reader.apps.stop_all()')
	StopApp = True
	cmd.close()
	evt.close()
	##conn.close()
	##mySocket.close()
	sys.close()