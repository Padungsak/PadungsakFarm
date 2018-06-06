import webiopi
#from enum import Enum

GPIO = webiopi.GPIO

class ValveImp:
    s_mcp2 = webiopi.deviceInstance("mcp2")
    m_valveStateList = {'Open':1,'Close':0,'Error':2}
    
    def __init__(self, a_valvePort, a_executionOrder):
        webiopi.debug('ValveImp  was added')  
        self.m_valvePort = int(a_valvePort)
        self.executionOrder = int(a_executionOrder)
        ValveImp.s_mcp2.setFunction(self.m_valvePort, GPIO.OUT)
        ValveImp.s_mcp2.digitalWrite(self.m_valvePort, GPIO.HIGH)
        self.valveState = ValveImp.m_valveStateList['Close']
        #self.CloseValve()
        
    def OpenValve(self):
        webiopi.sleep(1)
        webiopi.debug('*******************************************OpenValve2 called %d' % self.m_valvePort)
        ValveImp.s_mcp2.digitalWrite(self.m_valvePort, GPIO.LOW)
        self.valveState = ValveImp.m_valveStateList['Open']

    def CloseValve(self):
        webiopi.sleep(1)
        webiopi.debug('CloseValve2 called')
        ValveImp.s_mcp2.digitalWrite(self.m_valvePort, GPIO.HIGH)
        self.valveState = ValveImp.m_valveStateList['Close']
        
    def GetValveState(self):
        return self.valveState

    
