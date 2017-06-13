import webiopi

class SensorImp:

    def __init__(self, sensorChannal):
        self.sensorChannal = sensorChannal

    def GetValue(self):
        adc = webiopi.deviceInstance("adc")
        webiopi.debug('sensor voltage %d' % adc.analogReadVolt(self.sensorChannal))
        webiopi.debug('sensor value %d' % adc.analogRead(self.sensorChannal))
        return adc.analogRead(self.sensorChannal)
