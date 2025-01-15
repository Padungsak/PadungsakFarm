import webiopi
#from enum import Enum
import time,sys
sys.path.append('/home/pi/MyProject/python')
from constantRate import ConstantRate

GPIO = webiopi.GPIO

class ValveImp:
    m_valveStateList = {'Open':1,'Close':0,'Error':2}
    s_constRateObj = ConstantRate()
    #s_groundChemicalRate = float(s_constRateObj.GetRate("GroundChemicalRate"))
    #s_groundChemicalRateTime = int(s_constRateObj.GetRate("GroundChemicalRateTime"))
    
    def __init__(self, a_name, a_valvePort, a_chipNo, a_executionOrder):
        webiopi.debug('ValveImp  was added')
        self.m_name = a_name
        self.m_valvePort = int(a_valvePort)
        #self.m_chemicalPort = int(a_chipNo)
        self.m_chemicalConstVolume = int(ValveImp.s_constRateObj.GetRate(self.m_name))
        self.executionOrder = int(a_executionOrder)
        self.m_mcp = webiopi.deviceInstance("mcp%d" % a_chipNo)
        self.m_mcp.setFunction(self.m_valvePort, GPIO.OUT)
        self.m_mcp.digitalWrite(self.m_valvePort, GPIO.HIGH)
        #GPIO.setFunction(self.m_chemicalPort, GPIO.OUT)
        #GPIO.digitalWrite(self.m_chemicalPort, GPIO.HIGH)
        self.valveState = ValveImp.m_valveStateList['Close']
        #self.CloseValve()
        
    def OpenValve(self):
        webiopi.sleep(1)
        webiopi.debug('*******************************************OpenValve2 called %d' % self.m_valvePort)
        self.m_mcp.digitalWrite(self.m_valvePort, GPIO.LOW)
        self.valveState = ValveImp.m_valveStateList['Open']

    def CloseValve(self):
        webiopi.sleep(1)
        webiopi.debug('CloseValve2 called')
        self.m_mcp.digitalWrite(self.m_valvePort, GPIO.HIGH)
        self.valveState = ValveImp.m_valveStateList['Close']

    #def OpenChemicalValve(self):
    #   GPIO.digitalWrite(self.m_chemicalPort, GPIO.LOW)

    #def CloseChemicalValve(self):
    #    GPIO.digitalWrite(self.m_chemicalPort, GPIO.HIGH)
        
    def GetValveState(self):
        return self.valveState

    def GetChemicalConstVolume(self):
        return self.m_chemicalConstVolume

    def SetChemicalConstVolume(self, a_volume):
        self.m_chemicalConstVolume = int(a_value)
        ValveImp.s_constRateObj.UpdateRate(self.m_name, a_volume)

    #def GetGroundChemicalRate(self):
    #    return ValveImp.s_groundChemicalRate

    #def GetGroundChemicalRateTime(self):
    #    return ValveImp.s_groundChemicalRateTime
