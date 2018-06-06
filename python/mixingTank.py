import webiopi
import sys 
sys.path.append('/home/pi/MyProject/python')
from engine import EngineImp
from constantRate import ConstantRate

GPIO = webiopi.GPIO

class MixingTankImp:
    #s_mcp0 = webiopi.deviceInstance("mcp0")
    s_TankStateList = {'Pumping':1, 'Mixing':2, 'Close':0,'Error':-1}
    s_mixingTime = 30
    s_constRateObj = ConstantRate()

    def __init__(self, a_name, a_volumePort, a_rateTime):
        self.m_name = a_name
        self.m_volumePort = a_volumePort
        self.m_constFlowRate = MixingTankImp.s_constRateObj.GetRate(self.m_name)
        self.m_rateTime = a_rateTime
        self.m_volume = 0
        self.m_TankState = MixingTankImp.s_TankStateList['Close']
        self.m_errorMessage = ''
        GPIO.setFunction(self.m_volumePort, GPIO.IN)
        
    def TestFlowRate(self):
        EngineImp.getInstance().OpenWaterPump()
        webiopi.sleep(self.m_rateTime)
        EngineImp.getInstance().CloseWaterPump()
        
    def SetWaterVolume(self, a_volume):
        self.m_volume = a_volume
        webiopi.debug('SetWaterVolume %d' % self.m_volume)

    def SetWaterConstRate(self, a_value):
        self.m_constFlowRate = a_value
        MixingTankImp.s_constRateObj.UpdateRate(self.m_name, a_value)

    def ResetWaterVolume(self):
        self.m_volume = 0

    def GetWaterVolume(self):
        return str(self.m_volume) + "," + str(MixingTankImp.s_constRateObj.GetRate(self.m_name))

    def IsWaterEnough(self):
        return GPIO.digitalRead(self.m_volumePort) == GPIO.HIGH

    def IsMixingTankError(self):
        return self.m_TankState == MixingTankImp.s_TankStateList['Error']

    def GetErrorMessage(self):
        return self.m_errorMessage

    def Inspection(self):
        if self.m_volume <= 0:
            self.m_errorMessage = 'Please fill %s' % self.m_name
            return False
        else:
            if self.m_constFlowRate <= 0:
                self.m_errorMessage = 'Please fill constant flow rate for %s' % self.m_name
                return False
                
        return True

    def MixChemical(self):
        #Open water pump
        self.m_TankState = MixingTankImp.s_TankStateList['Pumping']
        EngineImp.getInstance().OpenWaterPump()
            
        l_flowRateConst = float(self.m_constFlowRate) / float(self.m_rateTime)
        l_rateCount = 0
        while l_rateCount < self.m_volume:
            l_rateCount += l_flowRateConst
            webiopi.sleep(1)

        EngineImp.getInstance().CloseWaterPump()
            
        self.m_TankState = MixingTankImp.s_TankStateList['Mixing']
        EngineImp.getInstance().OpenMixPump()
        webiopi.sleep(MixingTankImp.s_mixingTime)
        EngineImp.getInstance().CloseMixPump()
        self.m_TankState = MixingTankImp.s_TankStateList['Close']

