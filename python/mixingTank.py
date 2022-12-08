import webiopi
import sys 
sys.path.append('/home/pi/MyProject/python')
from engine import EngineImp
from constantRate import ConstantRate

GPIO = webiopi.GPIO

class MixingTankImp:
    s_TankStateList = {'Pumping':1, 'Mixing':2, 'Close':0,'Error':-1}
    #s_mixingTime = 120
    s_drainTime = 2000 
    s_constRateObj = ConstantRate()

    def __init__(self, a_name, a_volumeGpioPort, a_maxVolumeGpioPort, a_waterValveGpioPort, a_drainValveGpioPort, a_rateTime, a_initialWater):
        self.m_name = a_name
        self.m_volumeGpioPort = a_volumeGpioPort
        self.m_maxVolumeGpioPort = a_maxVolumeGpioPort
        self.m_waterValveGpioPort = a_waterValveGpioPort
        self.m_drainValveGpioPort = a_drainValveGpioPort
        self.m_constFlowRate = MixingTankImp.s_constRateObj.GetRate(self.m_name)
        self.m_rateTime = a_rateTime
        self.m_initialWater = a_initialWater
        self.m_volume = 0
        self.m_TankState = MixingTankImp.s_TankStateList['Close']
        self.m_errorMessage = ''
        GPIO.setFunction(self.m_volumeGpioPort, GPIO.IN)
        GPIO.setFunction(self.m_maxVolumeGpioPort, GPIO.IN)
        GPIO.setFunction(self.m_waterValveGpioPort, GPIO.OUT)
        GPIO.setFunction(self.m_drainValveGpioPort, GPIO.OUT)

    def DrainChemical(self):
        GPIO.digitalWrite(self.m_drainValveGpioPort, GPIO.LOW)
        while True:
            if self.IsWaterEnough():
                EngineImp.getInstance().OpenMixPump()
                webiopi.sleep(1)
                webiopi.debug("Draining water...")
                continue
            else:
                break
        
        EngineImp.getInstance().CloseMixPump()
        webiopi.sleep(MixingTankImp.s_drainTime)
        GPIO.digitalWrite(self.m_drainValveGpioPort, GPIO.HIGH)
       
        
        
    def TestFlowRate(self):
        GPIO.digitalWrite(self.m_waterValveGpioPort, GPIO.LOW)
        webiopi.sleep(1)
        EngineImp.getInstance().OpenWaterPump()
        webiopi.sleep(self.m_rateTime)
        EngineImp.getInstance().CloseWaterPump()
        webiopi.sleep(1)
        GPIO.digitalWrite(self.m_waterValveGpioPort, GPIO.HIGH)
        
    def SetWaterVolume(self, a_volume):
        self.m_volume = a_volume
        webiopi.debug('SetWaterVolume %f' % self.m_volume)

    def SetWaterConstRate(self, a_value):
        self.m_constFlowRate = a_value
        MixingTankImp.s_constRateObj.UpdateRate(self.m_name, a_value)

    def ResetWaterVolume(self):
        self.m_volume = 0

    def GetWaterVolume(self):
        return str(self.m_volume) + "," + str(MixingTankImp.s_constRateObj.GetRate(self.m_name))

    def IsWaterEnough(self):
        return GPIO.digitalRead(self.m_volumeGpioPort) == GPIO.HIGH

    def IsWaterOverflow(self):
        return GPIO.digitalRead(self.m_maxVolumeGpioPort) == GPIO.LOW

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

    def CompressWind(self, a_delayTime):
        self.m_TankState = MixingTankImp.s_TankStateList['Mixing']
        EngineImp.getInstance().OpenWindPump()
        webiopi.sleep(1)
        EngineImp.getInstance().OpenMixPump()
        webiopi.sleep(int(a_delayTime))
        EngineImp.getInstance().CloseMixPump()
        
    def OpenWaterPump(self, a_volume):
        GPIO.digitalWrite(self.m_waterValveGpioPort, GPIO.LOW)
        webiopi.sleep(3)
        EngineImp.getInstance().OpenWaterPump()
            
        l_flowRateConst = float(self.m_constFlowRate) / float(self.m_rateTime)
        l_rateCount = 0
        while l_rateCount < a_volume:
            l_rateCount += l_flowRateConst
            webiopi.debug('OpenWaterPump %d' % l_rateCount)
            webiopi.sleep(1)
            if self.IsWaterOverflow() == True:
                self.m_TankState = MixingTankImp.s_TankStateList['Error']
                break
                

        EngineImp.getInstance().CloseWaterPump()
        webiopi.sleep(1)
        GPIO.digitalWrite(self.m_waterValveGpioPort, GPIO.HIGH)
        
    def FillWater(self):
        #Open water pump
        self.m_TankState = MixingTankImp.s_TankStateList['Pumping']
        EngineImp.getInstance().OpenMixPump()
        l_volume =self.m_volume-self.m_initialWater
        self.OpenWaterPump(l_volume)
        #self.m_TankState = MixingTankImp.s_TankStateList['Close']
        EngineImp.getInstance().CloseMixPump()

    def InitialWater(self):
        self.m_TankState = MixingTankImp.s_TankStateList['Pumping']
        self.OpenWaterPump(self.m_initialWater)
        #self.m_TankState = MixingTankImp.s_TankStateList['Close']
        

    def CleanTank(self):
        self.DrainChemical()
        self.OpenWaterPump(self.m_volume)
        self.DrainChemical()
