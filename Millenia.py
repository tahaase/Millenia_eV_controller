import sys
import os
import serial 
import time
#from string import atoi

#Driver module for Newport's Spectra-Physics Millena eV CW laser.

class MilleniaeV:
    #Defines the port for the MILLENIA eV laser. In this case ttyACM0. NOTE: xon/xoff must be enabled. 
    def __init__(self, porteV='/dev/ttyACM0',baudVS=9600):
        self.eVport = serial.Serial(
            port = porteV,
            baudrate = baudVS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 5,
            xonxoff = True)
            
        
    #Opens the connection to the port.       
    def openConnection(self):
        self.eVport.close()
        self.eVport.open()
        vsOpen = self.eVport.isOpen()
        if vsOpen == True:
            print('connected to ', MilleniaeV().getID())
            #print('connected?')
        else:
            print('Error: Unable to connect to Millenia eV')
            exit()
            
    #Closes the connection to the port. 
    def closeConnection(self):
        self.eVport.close()  
        print('Connection to Millenia VS closed') 
    
    #Get ID.
    def getID(self):
        self.eVport.write(b'IDN?\r')
        #self.eVport.read(100)
        ID = self.eVport.readline()
        print(ID)
        return ID
        
    #Turns the laser ON    
    def turnON(self):
        self.eVport.write(b'On\r')
    #Turns the laser OFF    
    def turnOFF(self):
        self.eVport.write(b'OFF\r')
        
    #Open laser shutter.
    def openShutter(self):
        self.eVport.write(b'SHT:1\r')
    
    #Close laser shutter.     
    def closeShutter(self):
        self.eVport.write(b'SHT:0\r')

    def querryStatus(self):
        self.eVport.write(b'?F\r')
        msg = self.eVport.readline()
        print(msg)
    #Sets the laser to current mode for power meter optimaization.
    def setCurrentMode(self):
        self.eVport.write(b'M:0\r')
   
    #Sets the laser to power mode.     
    def setPowerMode(self):
        self.eVport.write(b'M:1\r')

    #Sets diode current
    def setPower(self, current):
        if (current<0):
            print('Current needs to be bigger than 0 A')
        else:
            msg = 'C1:'+str(current)+'\r'
            msg = msg.encode('utf-8')
            self.eVport.write(b'C1:'+current+'\r')        
    
    #Set laser power.
    def setPower(self, power):
        if (power>5 or power<0.3):
            print('Power needs to be in range of 0.3W to 5W')
        else:
            msg = 'P:'+str(power)+'\r'
            msg = msg.encode('utf-8')
            self.eVport.write(msg)        

    def querryLaserPower(self):
        self.eVport.write(b'?P\r')
        p = self.eVport.readline()
        print(p)
       
    #Querries the laser for the current in diode 1
    def querryDiodeCurrent(self):
        self.eVport.write(b'?CS1\r')
        current = self.eVport.readline()
        print(current)
      
    def querryMode(self):
        self.eVport.write(b'?M\r')
        modeResponse = self.eVport.readline()
        if modeResponse == '1':    
            mode = 'Power'
        else:
            mode = 'Current'
        print(mode)

    def shutterStatus(self):
        self.eVport.write(b'?SHT\r')
        shutterVal = 'not modified'
        shutterVal = self.eVport.readline()
        if shutterVal == '1':
            shutter = 'Open'
        else: 
            shutter = 'Closed'
        print(shutterVal)            
