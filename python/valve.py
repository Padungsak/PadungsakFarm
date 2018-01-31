import webiopi
import datetime
import timeit
#from enum import Enum

GPIO = webiopi.GPIO

class ValveImp:

    m_limitTimeForRotateMotor = 45 #count in second
    m_valveStateList = {'Open':1,'Close':0,'Error':2}
    
    def __init__(self, a_relayPort1, a_relayPort2, a_switchPort, a_executionOrder, a_isNewValve):
        webiopi.debug('ValveImp  was added')  
        self.relayPort1 = a_relayPort1
        self.relayPort2 = a_relayPort2
        self.switchPort = a_switchPort
        webiopi.debug(self.relayPort1)
        webiopi.debug(self.relayPort2)
        self.executionOrder = int(a_executionOrder)
        if(a_isNewValve == 'true'):
            self.isNewValve = True
        else:
            self.isNewValve = False
        GPIO.setFunction(self.switchPort, GPIO.IN)
        GPIO.setFunction(self.relayPort1, GPIO.OUT)
        GPIO.setFunction(self.relayPort2, GPIO.OUT)
        #GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
        #GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
        self.valveState = ValveImp.m_valveStateList['Close']
        #self.CloseValve()
        
    def OpenValve(self):
        if(self.isNewValve == True):
            self.OpenValve2()
        else:
            self.OpenValve1()
        
    def OpenValve1(self):
        webiopi.debug('OpenValve1 called')
        if (GPIO.digitalRead(self.switchPort) == True):
            self.valveState = ValveImp.m_valveStateList['Error']
            GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
            GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
            return
        
        webiopi.debug(self.relayPort1)
        webiopi.debug(self.relayPort2)
        GPIO.digitalWrite(self.relayPort1, GPIO.HIGH)
        GPIO.digitalWrite(self.relayPort2, GPIO.LOW)

        l_startTime = timeit.default_timer()
        while True:
            webiopi.debug(GPIO.digitalRead(self.switchPort))
            if (GPIO.digitalRead(self.switchPort) == True):
                GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
                GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
                webiopi.debug('Open switch tricked')
                break
            webiopi.sleep(0.8)
            if((timeit.default_timer() - l_startTime) > ValveImp.m_limitTimeForRotateMotor):
                self.valveState = ValveImp.m_valveStateList['Error']
                GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
                GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
                webiopi.debug('Valve error!')
                webiopi.debug(self.valveState)
                return
                

        webiopi.sleep(1)
        webiopi.debug('Inverse motor direction')
        GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
        GPIO.digitalWrite(self.relayPort2, GPIO.HIGH)
        l_startTime = timeit.default_timer()
        while True:
            if (GPIO.digitalRead(self.switchPort) == False):
                webiopi.sleep(0.5)
                GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
                GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
                webiopi.debug('Open switch released')
                break
            webiopi.sleep(0.5)
            if((timeit.default_timer() - l_startTime) > ValveImp.m_limitTimeForRotateMotor):
                self.valveState = ValveImp.m_valveStateList['Error']
                GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
                GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
                return

        self.valveState = ValveImp.m_valveStateList['Open']

    def OpenValve2(self):
        webiopi.debug('OpenValve2 called')
        GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
        self.valveState = ValveImp.m_valveStateList['Open']

    def CloseValve(self):
        if(self.isNewValve == True):
            self.CloseValve2()
        else:
            self.CloseValve1()

    def CloseValve1(self):
        webiopi.debug('CloseValve1 called')
        if (GPIO.digitalRead(self.switchPort) == True):
            self.valveState = ValveImp.m_valveStateList['Error']
            GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
            GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
            return
        
        GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
        GPIO.digitalWrite(self.relayPort2, GPIO.HIGH)

        l_startTime = timeit.default_timer()
        while True:
            webiopi.debug(GPIO.digitalRead(self.switchPort))
            if (GPIO.digitalRead(self.switchPort) == True):
                GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
                GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
                webiopi.debug('Close switch tricked')
                break
            webiopi.sleep(0.8)
            if((timeit.default_timer() - l_startTime) > ValveImp.m_limitTimeForRotateMotor):
                self.valveState = ValveImp.m_valveStateList['Error']
                GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
                GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
                return

        webiopi.sleep(1)
        webiopi.debug('Inverse motor direction')
        GPIO.digitalWrite(self.relayPort1, GPIO.HIGH)
        GPIO.digitalWrite(self.relayPort2, GPIO.LOW)

        l_startTime = timeit.default_timer()
        while True:
            if (GPIO.digitalRead(self.switchPort) == False):
                webiopi.sleep(0.5)
                GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
                GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
                webiopi.debug('Close switch released')
                break
            webiopi.sleep(0.5)
            if((timeit.default_timer() - l_startTime) > ValveImp.m_limitTimeForRotateMotor):
                self.valveState = ValveImp.m_valveStateList['Error']
                GPIO.digitalWrite(self.relayPort1, GPIO.LOW)
                GPIO.digitalWrite(self.relayPort2, GPIO.LOW)
                return

        self.valveState = ValveImp.m_valveStateList['Close']

    def CloseValve2(self):
        webiopi.debug('CloseValve2 called')
        GPIO.digitalWrite(self.relayPort1, GPIO.HIGH)
        self.valveState = ValveImp.m_valveStateList['Close']
        
    def GetValveState(self):
        return self.valveState

    
