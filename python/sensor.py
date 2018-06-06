import webiopi
import time
from math import exp

GPIO = webiopi.GPIO

class SensorImp:

    def __init__(self, sensorChannal):
        self.sensorChannal = sensorChannal

    def GetValue(self):
        adc = webiopi.deviceInstance("adc")
        #webiopi.debug('sensor voltage %d' % adc.analogReadVolt(self.sensorChannal))
        #webiopi.debug('sensor value %d' % adc.analogRead(self.sensorChannal))
        return adc.analogRead(self.sensorChannal)

class UltraSonicImp:

    def __init__(self, a_sensorChannal):
        self.sensorChannal = a_sensorChannal

    def GetDistance(self):
        adc = webiopi.deviceInstance("adc")
        voltRef = adc.analogReference()
        voltRet = adc.analogReadVolt(self.sensorChannal)
        #resolution = adc.analogResolution()
        adcMax = adc.analogMaximum()
        adcRet = adc.analogRead(self.sensorChannal)
        #webiopi.debug('analogReference %f' % voltRef)
        #webiopi.debug('analogReadVolt %f' % voltRet)
        #webiopi.debug('analogResolution %f' % resolution)
        #webiopi.debug('analogRead %f' % adcRet)
        #webiopi.debug('analogMaximum %f' % adcMax)
        #distance = ((adcRet*1024)/(adcMax))*(voltRet/voltRef)
        distance =  19.5 - round((adcRet*19.5)/835,1)
        value = round(distance * 7.5 * 7.5,1)
        webiopi.debug('adcRet test  %f' % adcRet)
        webiopi.debug('Distance test  %f' % distance)
        webiopi.debug('Value test  %f' % value)
        return distance
        #return 1024*(voltRet/voltRef)/10
        #distance = voltRet
        #return distance
