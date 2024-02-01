import webiopi
import time,sys
sys.path.append('/home/pi/MyProject/python')
from constantRate import ConstantRate
from chemicalOrderNum import ChemicalOrderNum


GPIO = webiopi.GPIO

class ChemicalTankImp:
    s_TankStateList = {'Pumping':1,'Close':0,'Error':-1}
    s_countingConfirmation = 4
    s_constRateObj = ConstantRate()
    s_orderNumObj = ChemicalOrderNum()
    s_waterCleanTubeName = "WaterCleanTube"
    s_waterCleanTubeRound = 5
	
    def __init__(self, a_name, a_gpioSealedValve, a_chipNo, a_motorPortNum, a_volumePortNum, a_rateTime, a_isNC):
        webiopi.debug('ChemicalTankImp create!!')
        self.m_name = a_name
        self.m_gpioSealedValve = a_gpioSealedValve
        self.m_mcp = webiopi.deviceInstance("mcp%d" % a_chipNo)
        self.m_motorPortNum = a_motorPortNum
        self.m_volumePortNum = a_volumePortNum
        self.m_constFlowRate = ChemicalTankImp.s_constRateObj.GetRate(self.m_name)
        self.m_orderNum = ChemicalTankImp.s_orderNumObj.GetOrder(self.m_name)
        self.m_rateTime = a_rateTime
        if a_isNC == 0:
            self.chemicalNeedLogic = GPIO.LOW
        else:
            self.chemicalNeedLogic = GPIO.HIGH
        
        self.m_isNC = a_isNC
        self.m_volume = 0
        self.m_TankState = ChemicalTankImp.s_TankStateList['Close']
        self.m_errorMessage = ''
        self.m_mcp.setFunction(self.m_volumePortNum, GPIO.IN)
        self.m_mcp.setFunction(self.m_motorPortNum, GPIO.OUT)    
        self.m_mcp.digitalWrite(self.m_motorPortNum, GPIO.HIGH)
        GPIO.setFunction(self.m_gpioSealedValve, GPIO.OUT)
        GPIO.digitalWrite(self.m_gpioSealedValve, GPIO.HIGH)
        

    def TestFlowRate(self):
        webiopi.debug("TestFlowRate was called !!!!!!")
        GPIO.digitalWrite(self.m_gpioSealedValve, GPIO.LOW)
        webiopi.sleep(3)
        self.m_mcp.digitalWrite(self.m_motorPortNum, GPIO.LOW)
        webiopi.sleep(self.m_rateTime)
        self.m_mcp.digitalWrite(self.m_motorPortNum, GPIO.HIGH)
        webiopi.sleep(3)
        GPIO.digitalWrite(self.m_gpioSealedValve, GPIO.HIGH)
        
    def SetChemicalVolume(self, a_volume):
        self.m_volume = a_volume
        webiopi.debug('SetChemicalVolume %f' % self.m_volume)

    def SetChemicalConstRate(self, a_value, a_order):
        self.m_constFlowRate = a_value
        ChemicalTankImp.s_constRateObj.UpdateRate(self.m_name, a_value)
        ChemicalTankImp.s_orderNumObj.UpdateOrder(self.m_name, a_order)

    def ResetChemicalVolume(self):
        self.m_volume = 0

    def GetChemicalVolume(self):
        return str(self.m_volume) + "," + str(ChemicalTankImp.s_constRateObj.GetRate(self.m_name)) + "," + str(ChemicalTankImp.s_orderNumObj.GetOrder(self.m_name))

    def StopPump(self):
        self.m_mcp.digitalWrite(self.m_motorPortNum, GPIO.HIGH)
        
    def GetErrorMessage(self):
        return self.m_errorMessage

    def Inspection(self):
        if self.m_volume > 0 and self.m_constFlowRate <= 0:
            self.m_errorMessage = 'Please fill constant flow rate for %s' % self.m_name
            return False
        return True

    def IsVolumeSet(self):
        if self.m_volume > 0:
            return True
        return False
        
    def FillChemical(self):
        webiopi.debug('Call FillChemical')
        webiopi.debug('Volume = %d' % self.m_volume)
        if self.m_volume > 0:
            webiopi.sleep(2)
            GPIO.digitalWrite(self.m_gpioSealedValve, GPIO.LOW)
            webiopi.sleep(3)
            self.m_mcp.digitalWrite(self.m_motorPortNum, GPIO.LOW)
            self.m_TankState = ChemicalTankImp.s_TankStateList['Pumping']

            l_flowRateConst = float(self.m_constFlowRate) / float(self.m_rateTime)
            l_rateCount = 0
            while l_rateCount < self.m_volume:
                l_rateCount += l_flowRateConst
                webiopi.sleep(1)
                webiopi.debug('Chemical rate count = %f' % l_rateCount)
                    
            self.m_mcp.digitalWrite(self.m_motorPortNum, GPIO.HIGH)
            webiopi.sleep(3)
            GPIO.digitalWrite(self.m_gpioSealedValve, GPIO.HIGH)
            self.m_TankState = ChemicalTankImp.s_TankStateList['Close']
		
    def IsChemicalTankError(self):
        return self.m_TankState == ChemicalTankImp.s_TankStateList['Error']

    def IsChemicalInTankEnough(self):
        webiopi.debug('IsChemicalInTankEnough %d = ' % self.m_volumePortNum)
        if self.m_mcp.digitalRead(self.m_volumePortNum) == GPIO.LOW:
            webiopi.debug('GPIO.LOW')
        else:
            webiopi.debug('GPIO.HIGH')
        return self.m_mcp.digitalRead(self.m_volumePortNum) != self.chemicalNeedLogic

    def NeedToFillChemical(self):
        if self.m_volume > 0:
            if self.m_mcp.digitalRead(self.m_volumePortNum) == self.chemicalNeedLogic:
                return True
            else:
                #Work around for reding bug in MCP23017
                l_countingConfirmation = 0
                while l_countingConfirmation <= ChemicalTankImp.s_countingConfirmation:
                    webiopi.sleep(0.5)
                    webiopi.debug('Error mcp23017 in while loop!!!')
                    if self.m_mcp.digitalRead(self.m_volumePortNum) == self.chemicalNeedLogic:
                        return True
                    l_countingConfirmation = l_countingConfirmation +1
                
        return False

    def IsWaterCleanTube(self):
        return self.m_name == self.s_waterCleanTubeName
    
    def CleanChemicalTube(self):
        for l_num in range(self.s_waterCleanTubeRound):
            self.FillChemical()
        