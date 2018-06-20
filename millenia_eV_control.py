"""
Required packages
"""
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#sys.modules['PyQt4.QtGui'] = PySide.QtGui
import os
import serial
import time
#import numpy as np
"""
Import GUI elements
"""
import millenia_ev_window


"""
Import other files
"""
"""
Main define
"""
app = QApplication(sys.argv)
    
class MainDialog(QMainWindow, millenia_ev_window.Ui_Millenia_eV):
    def __init__(self, parent = None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        
        """
        Initialize laser 
        """
        self.eV_laser = Millenia_eV_Laser()
        self.eV_laser.openConnection()
        self.eV_laser.setPower(0)
        self.eV_laser.setPowerMode()
        self.eV_laser.closeShutter()      
        self.eV_laser.turnOFF()
        self.vs_emission.setValue(0)
        self.vs_shutter.setValue(0)
        
        """
        Initialize status checking
        """
        self.status_check = Laser_Status(self.eV_laser)
        if (self.eV_laser.port_open):
          self.status_check.start()
        """
        Define Variables
        """
        self.alignment_mode = False
        self.pb_powerMode.setDisabled(True)
        self.the_font = QFont("Times",20,QFont.Bold)
        self.label_mode.setFont(self.the_font)
        self.label_status.setFont(self.the_font)
        """
        DEFINE CONNECTIONS
        """     
        self.vs_emission.valueChanged.connect(self.laser_emission)
        self.vs_shutter.valueChanged.connect(self.shutter_changed)
        self.sb_Power.valueChanged.connect(self.power_change)
        self.pb_send.clicked.connect(self.send_msg)
        self.pb_alignment.clicked.connect(self.enter_alignment_mode)
        self.pb_powerMode.clicked.connect(self.enter_power_mode)
        
        self.status_check.signal_status.connect(self.set_status_info, Qt.QueuedConnection)
        self.status_check.signal_power.connect(self.set_status_info, Qt.QueuedConnection)
        
    
    """
    Functions
    """
    def laser_emission(self):
        if (self.vs_emission.value() == 1):
          self.eV_laser.turnON()
        if (self.vs_emission.value() == 0):
          self.eV_laser.turnOFF()
          self.vs_shutter.setValue(0)
    
    def shutter_changed(self):
      #print(self.vs_shutter.value())
      if (self.vs_shutter.value() == 1):
        self.eV_laser.openShutter()
      if (self.vs_shutter.value() == 0):
        self.eV_laser.closeShutter()
        
    def power_change(self):
      self.eV_laser.setPower(self.sb_Power.value())
      
    def set_status_info(self):
      if (self.eV_laser.port_open == False):
        self.label_status.setText('Cannot Connect')
      else:
        val = (self.status_check.status).decode('utf-8')
        self.label_status.setText(val)
        val = float((self.status_check.power).decode('utf-8'))
        self.lcd_power.display(val)
        
    def send_msg(self):
      msg = str(self.tb_send.text())
      self.tb_sent.append(msg)
      msg = (msg+'\r').encode('utf-8')
      self.eV_laser.eVport.write(msg)
      self.tb_send.clear()
      msg = (self.eV_laser.eVport.readline()).decode('utf-8')
      self.tb_recieved.append(msg)
      
    def enter_alignment_mode(self):
      self.eV_laser.turnOFF()
      self.vs_emission.setValue(0)
      self.vs_shutter.setValue(0)
      self.eV_laser.setCurrentMode()
      msg = int((self.eV_laser.querryMode()).decode('utf-8'))
      if(msg == 0):
        self.eV_laser.setCurrent(2)
        msg = float((self.eV_laser.querryDiodeCurrent()).decode('utf-8'))
        if(msg == 2.00):
          self.alignment_mode = True
          self.pb_alignment.setDisabled(True)
          self.pb_powerMode.setEnabled(True)
          self.label_mode.setText('Alignment')
               
    def enter_power_mode(self):
     if(self.alignment_mode == True):
       self.eV_laser.turnOFF()
       self.vs_emission.setValue(0)
       self.vs_shutter.setValue(0)
       self.eV_laser.setPowerMode()
       msg = int((self.eV_laser.querryMode()).decode('utf-8'))
       if(msg == 1):
         self.alignment_mode = False
         self.pb_alignment.setEnabled(True)
         self.pb_powerMode.setDisabled(True)
         self.label_mode.setText('Power Mode')
         
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.eV_laser.closeShutter()
            self.eV_laser.turnOFF()
            self.eV_laser.closeConnection()            
            event.accept()
        else:
            event.ignore()
         
class Millenia_eV_Laser():
    #Defines the port for the MILLENIA eV laser. In this case ttyACM0. NOTE: xon/xoff must be enabled. 
    def __init__(self, porteV='/dev/ttyACM0',baudVS=9600):
        self.eVport = serial.Serial(
            port = porteV,
            baudrate = baudVS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 0.5,
            xonxoff = True)           
        self.port_open = False
    #Opens the connection to the port.       
    
    def openConnection(self):
        self.eVport.close()
        self.eVport.open()
        self.port_open = self.eVport.isOpen()
        if self.port_open == True:
            print('connected to ', self.getID())
            #print('connected')
        else:
            print('Error: Unable to connect to Millenia eV')
            exit()
            
    #Closes the connection to the port. 
    def closeConnection(self):
        self.eVport.close()  
        print('Connection to Millenia VS closed') 
    
    #Get ID.
    def getID(self):
        self.eVport.write(b'*IDN?\r')
        #self.eVport.read(100)
        ID = self.eVport.readline()
        return ID
        print(ID)
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
        status = self.eVport.readline()
        return status
        
    #Sets the laser to current mode for power meter optimaization.
    def setCurrentMode(self):
        self.eVport.write(b'M:0\r')
   
    #Sets the laser to power mode.     
    def setPowerMode(self):
        self.eVport.write(b'M:1\r')

    #Sets diode current
    def setCurrent(self, current):
        if (current<0):
            print('Current needs to be bigger than 0 A')
        else:
            msg = 'C1:'+str(current)+'\r'
            msg = msg.encode('utf-8')
            self.eVport.write(msg)        
    
    #Set laser power.
    def setPower(self, power):
        if (power>5 or power<0):
            print('Power needs to be in range of 0 to 5W')
        else:
            msg = 'P:'+str(power)+'\r'
            msg = msg.encode('utf-8')
            self.eVport.write(msg)        

    def querryLaserPower(self):
        self.eVport.write(b'?P\r')
        p = self.eVport.readline()
        #print(p)
        return p
       
    #Querries the laser for the current in diode 1
    def querryDiodeCurrent(self):
        self.eVport.write(b'?CS1\r')
        current = self.eVport.readline()
        return(current)
      
    def querryMode(self):
        self.eVport.write(b'?M\r')
        mode = self.eVport.readline()
        return(mode)
    
    def shutterStatus(self):
        self.eVport.write(b'?SHT\r')
        shutterVal = self.eVport.readline()
        return(shutterVal)
    
class Laser_Status(QThread):
    signal_status = pyqtSignal(int)
    signal_power = pyqtSignal(int) 
    
    def __init__(self, eV_laser):
        #super(TCPIP_Host, self).__init__(parent)
        QThread.__init__(self,parent = app)
        self.status = 0
        self.power = 0
        self.update = False
        self.port = eV_laser
    def run(self):
      self.update = True
      while (self.update and self.port.port_open):
        self.status = self.port.querryStatus()
        self.power = self.port.querryLaserPower()
        self.signal_status.emit(self.status)
        self.signal_power.emit(self.power)   
        time.sleep(1)
        
def main():
    millenia_control = MainDialog()
    millenia_control.show()
    app.exec_()
       
if __name__ == "__main__":
    main()

