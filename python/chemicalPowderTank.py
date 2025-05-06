import webiopi
import time,sys
sys.path.append('/home/pi/MyProject/python')
from constantRate import ConstantRate
from chemicalOrderNum import ChemicalOrderNum

GPIO = webiopi.GPIO

class ChemicalPowderTankImp:
    s_powderTankStateList = {'Pumping':1,'Close':0,'Error':-1}
    s_constRateObj = ConstantRate()
    s_orderNumObj = ChemicalOrderNum()
    
    def __init__(self, a_name, a_chipNo, a_mcpPumpMotorPort, a_mcpMixingMotorPort, a_rateTime):
        self.m_name = a_name
        self.m_mcp = webiopi.deviceInstance("mcp%d" % a_chipNo)
        self.m_mcpPumpMotorPort = a_mcpPumpMotorPort
        self.m_mcpMixingMotorPort = a_mcpMixingMotorPort
        self.m_constFlowRate = ChemicalPowderTankImp.s_constRateObj.GetRate(self.m_name)
        self.m_orderNum = ChemicalPowderTankImp.s_orderNumObj.GetOrder(self.m_name)
        self.m_rateTime = a_rateTime

        self.m_volume = 0
        self.m_powderTankState = ChemicalPowderTankImp.s_powderTankStateList['Close']
        self.m_errorMessage = ''
        self.m_mcp.setFunction(self.m_mcpPumpMotorPort, GPIO.OUT)
        self.m_mcp.digitalWrite(self.m_mcpPumpMotorPort, GPIO.HIGH)
        self.m_mcp.setFunction(self.m_mcpMixingMotorPort, GPIO.OUT)
        self.m_mcp.digitalWrite(self.m_mcpMixingMotorPort, GPIO.HIGH)
        webiopi.debug('ChemicalPowderTankImp create!!')
		
    def SetChemicalVolume(self, a_volume):
        self.m_volume = a_volume
        webiopi.debug('SetChemicalVolume %f' % self.m_volume)
		
    def SetChemicalConstRate(self, a_value, a_order):
        self.m_constFlowRate = a_value
        ChemicalPowderTankImp.s_constRateObj.UpdateRate(self.m_name, a_value)
        ChemicalPowderTankImp.s_orderNumObj.UpdateOrder(self.m_name, a_order)
		
    def ResetChemicalVolume(self):
        self.m_volume = 0
		
    def GetChemicalVolume(self):
        return str(self.m_volume) + "," + str(ChemicalPowderTankImp.s_constRateObj.GetRate(self.m_name)) + "," + str(ChemicalPowderTankImp.s_orderNumObj.GetOrder(self.m_name))
		
    def GetErrorMessage(self):
        return self.m_errorMessage
		
    def Inspection(self):
        if self.m_volume > 0 and self.m_constFlowRate <= 0:
            self.m_errorMessage = 'Please fill constant powderTank rate for %s' % self.m_name
            return False
        return True
		
    def IsVolumeSet(self):
        if self.m_volume > 0:
            return True
        return False
    
    def IsChemicalPowderTankError(self):
        return self.m_powderTankState == ChemicalPowderTankImp.s_powderTankStateList['Error']
    
    def IsChemicalInTankEnough(self):    
        return True
    
    def StopPowderTank(self):
        self.m_mcp.digitalWrite(self.m_mcpPumpMotorPort, GPIO.HIGH)
        webiopi.sleep(1)
        self.m_mcp.digitalWrite(self.m_mcpMixingMotorPort, GPIO.HIGH)
        
    def TestFlowRate(self):
        webiopi.debug("TestFlowRate was called !!!!!!")
        self.m_mcp.digitalWrite(self.m_mcpMixingMotorPort, GPIO.LOW)
        webiopi.sleep(5)
        self.m_mcp.digitalWrite(self.m_mcpPumpMotorPort, GPIO.LOW)
        webiopi.sleep(self.m_rateTime)
        self.m_mcp.digitalWrite(self.m_mcpPumpMotorPort, GPIO.HIGH)
        webiopi.sleep(1)
        self.m_mcp.digitalWrite(self.m_mcpMixingMotorPort, GPIO.HIGH)
    
    def FillPowderChemical(self):
         webiopi.debug('Call FillPowderChemical')
         webiopi.debug('Volume = %d' % self.m_volume)
         if self.m_volume > 0:
             self.m_mcp.digitalWrite(self.m_mcpMixingMotorPort, GPIO.LOW)
             webiopi.sleep(5)
             self.m_mcp.digitalWrite(self.m_mcpPumpMotorPort, GPIO.LOW)
             self.m_powderTankState = ChemicalPowderTankImp.s_powderTankStateList['Pumping']

             l_flowRateConst = float(self.m_constFlowRate) / float(self.m_rateTime)
             l_rateCount = 0
             while l_rateCount < self.m_volume:
                 l_rateCount += l_flowRateConst
                 webiopi.sleep(1)
                 webiopi.debug('Chemical rate count = %f' % l_rateCount)
                    
             self.m_mcp.digitalWrite(self.m_mcpPumpMotorPort, GPIO.HIGH)
             webiopi.sleep(2)
             self.m_mcp.digitalWrite(self.m_mcpMixingMotorPort, GPIO.HIGH)
             webiopi.sleep(3)
             self.m_TankState = ChemicalPowderTankImp.s_powderTankStateList['Close']
