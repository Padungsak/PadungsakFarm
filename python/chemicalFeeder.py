import webiopi
import time,sys
sys.path.append('/home/pi/MyProject/python')
from constantRate import ConstantRate
from chemicalOrderNum import ChemicalOrderNum

GPIO = webiopi.GPIO

class ChemicalFeederImp:
    s_feederStateList = {'Pumping':1,'Close':0,'Error':-1}
    s_countingConfirmation = 4
    s_inFeedDelayOffset=4
    s_constRateObj = ConstantRate()
    s_orderNumObj = ChemicalOrderNum()
    s_chemicalNeedLogic = GPIO.LOW
	
    def __init__(self, a_name, a_chipNo, a_motorPortNum1, a_motorPortNum2, a_mcpMotorEnablePort, a_mcpShakePort, a_mcpShakeEnablePort, a_feedTime):
        self.m_name = a_name
        self.m_mcp = webiopi.deviceInstance("mcp%d" % a_chipNo)
        self.m_motorPortNum1 = a_motorPortNum1
        self.m_motorPortNum2 = a_motorPortNum2
        self.m_mcpMotorEnablePort = a_mcpMotorEnablePort
        self.m_mcpShakePort = a_mcpShakePort
        self.m_mcpShakeEnablePort = a_mcpShakeEnablePort
        self.m_constFeedRate = ChemicalFeederImp.s_constRateObj.GetRate(self.m_name)
        self.m_orderNum = ChemicalFeederImp.s_orderNumObj.GetOrder(self.m_name)
        self.m_feedTime = a_feedTime

        self.m_volume = 0
        self.m_feederState = ChemicalFeederImp.s_feederStateList['Close']
        self.m_errorMessage = ''
        self.m_mcp.setFunction(self.m_motorPortNum1, GPIO.OUT)
        self.m_mcp.digitalWrite(self.m_motorPortNum1, GPIO.LOW)
        self.m_mcp.setFunction(self.m_motorPortNum2, GPIO.OUT)
        self.m_mcp.digitalWrite(self.m_motorPortNum2, GPIO.LOW)
        self.m_mcp.setFunction(self.m_mcpMotorEnablePort, GPIO.OUT)
        self.m_mcp.digitalWrite(self.m_mcpMotorEnablePort, GPIO.LOW)
        self.m_mcp.setFunction(self.m_mcpShakePort, GPIO.OUT)
        self.m_mcp.digitalWrite(self.m_mcpShakePort, GPIO.LOW)
        self.m_mcp.setFunction(self.m_mcpShakeEnablePort, GPIO.OUT)
        self.m_mcp.digitalWrite(self.m_mcpShakeEnablePort, GPIO.LOW)
        webiopi.debug('ChemicalFeederImp create!!')
		
    def SetChemicalVolume(self, a_volume):
        self.m_volume = a_volume
        webiopi.debug('SetChemicalVolume %f' % self.m_volume)
		
    def SetChemicalConstRate(self, a_value, a_order):
        self.m_constFeedRate = a_value
        ChemicalFeederImp.s_constRateObj.UpdateRate(self.m_name, a_value)
        ChemicalFeederImp.s_orderNumObj.UpdateOrder(self.m_name, a_order)
		
    def ResetChemicalVolume(self):
        self.m_volume = 0
		
    def GetChemicalVolume(self):
        return str(self.m_volume) + "," + str(ChemicalFeederImp.s_constRateObj.GetRate(self.m_name)) + "," + str(ChemicalFeederImp.s_orderNumObj.GetOrder(self.m_name))
		
    def GetErrorMessage(self):
        return self.m_errorMessage
		
    def Inspection(self):
        if self.m_volume > 0 and self.m_constFeedRate <= 0:
            self.m_errorMessage = 'Please fill constant feed rate for %s' % self.m_name
            return False
        return True
		
    def IsVolumeSet(self):
        if self.m_volume > 0:
            return True
        return False
		
    def IsChemicalFeedError(self):
        return self.m_feedState == ChemicalFeedImp.s_feedStateList['Error']
		
    def IsChemicalInTankEnough(self):    
        #return self.m_mcp.digitalRead(self.m_volumePortNum) != ChemicalFeedImp.s_chemicalNeedLogic
        return True
		
    def StopFeeder(self):
        self.m_mcp.digitalWrite(self.m_motorPortNum1, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_motorPortNum2, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_mcpMotorEnablePort, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_mcpShakePort, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_mcpShakeEnablePort, GPIO.LOW)

    def GetChemical(self):
        self.m_mcp.digitalWrite(self.m_mcpShakePort, GPIO.HIGH)
        webiopi.sleep(1)
        self.m_mcp.digitalWrite(self.m_mcpShakeEnablePort, GPIO.HIGH)
        webiopi.sleep(1)
        
        self.m_mcp.digitalWrite(self.m_motorPortNum1, GPIO.HIGH)
        self.m_mcp.digitalWrite(self.m_motorPortNum2, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_mcpMotorEnablePort, GPIO.HIGH)
        webiopi.sleep(self.m_feedTime)
        self.m_mcp.digitalWrite(self.m_motorPortNum1, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_motorPortNum2, GPIO.HIGH) 
        webiopi.sleep(self.m_feedTime)

        self.m_mcp.digitalWrite(self.m_mcpMotorEnablePort, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_motorPortNum1, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_motorPortNum2, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_mcpShakeEnablePort, GPIO.LOW)
        self.m_mcp.digitalWrite(self.m_mcpShakePort, GPIO.LOW)


    def TestFeedRate(self):
        webiopi.debug("TestFeedRate was called !!!!!!")
        self.GetChemical()
        webiopi.debug("TestFeedRate was stopped !!!!!!")
        		
    def FeedChemical(self):
        webiopi.debug('Call FeedChemical')
        webiopi.debug('Volume = %d' % self.m_volume)
        if self.m_volume > 0:
            self.m_feederState = ChemicalFeederImp.s_feederStateList['Pumping']

            l_feedVol = self.m_volume
            while l_feedVol > 0:
                self.GetChemical()
                l_feedVol = l_feedVol - self.m_constFeedRate
