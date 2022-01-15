import webiopi

GPIO = webiopi.GPIO

class EngineImp:

    s_instance = None
    
    @staticmethod
    def getInstance():
        if EngineImp.s_instance == None:
            EngineImp()
        return EngineImp.s_instance

        
    def __init__(self):
        if EngineImp.s_instance != None:
           raise Exception("This class is singleton Please call getInstance!")
        else:
           EngineImp.s_instance = self
        

    def Initialization(self, a_waterPumpGpioPort, a_chemicalPumpGpioPort, a_windPumpGpioPort, a_mixGpioPort, a_coconutWaterPumpPort):
        self.m_waterPumpGpioPort = a_waterPumpGpioPort
        self.m_chemicalPumpGpioPort = a_chemicalPumpGpioPort
        self.m_windPumpGpioPort = a_windPumpGpioPort
        self.m_mixGpioPort = a_mixGpioPort
        self.m_coconutWaterPumpPort = a_coconutWaterPumpPort
        GPIO.setFunction(self.m_waterPumpGpioPort, GPIO.OUT)
        GPIO.setFunction(self.m_chemicalPumpGpioPort, GPIO.OUT)
        GPIO.setFunction(self.m_windPumpGpioPort, GPIO.OUT)
        GPIO.setFunction(self.m_mixGpioPort, GPIO.OUT)
        GPIO.setFunction(self.m_coconutWaterPumpPort, GPIO.OUT)
        
    def OpenWaterPump(self):
        GPIO.digitalWrite(self.m_waterPumpGpioPort, GPIO.LOW)        

    def CloseWaterPump(self):
        GPIO.digitalWrite(self.m_waterPumpGpioPort, GPIO.HIGH)

    def OpenChemicalPump(self):
        GPIO.digitalWrite(self.m_chemicalPumpGpioPort, GPIO.LOW)

    def CloseChemicalPump(self):
        GPIO.digitalWrite(self.m_chemicalPumpGpioPort, GPIO.HIGH)

    def OpenWindPump(self):
        GPIO.digitalWrite(self.m_windPumpGpioPort, GPIO.LOW)

    def CloseWindPump(self):
        GPIO.digitalWrite(self.m_windPumpGpioPort, GPIO.HIGH)

    def OpenMixPump(self):
        GPIO.digitalWrite(self.m_mixGpioPort, GPIO.LOW)

    def CloseMixPump(self):
        GPIO.digitalWrite(self.m_mixGpioPort, GPIO.HIGH)

    def OpenCoconutPump(self):
        GPIO.digitalWrite(self.m_coconutWaterPumpPort, GPIO.LOW)

    def CloseCoconutPump(self):
        GPIO.digitalWrite(self.m_coconutWaterPumpPort, GPIO.HIGH)
        
    def CloseAllEngine(self):
        self.CloseWaterPump()
        webiopi.sleep(0.5)
        self.CloseChemicalPump()
        webiopi.sleep(0.5)
        self.CloseWindPump()
        webiopi.sleep(0.5)
        self.CloseMixPump()
        webiopi.sleep(0.5)
        self.CloseCoconutPump()
        webiopi.sleep(0.5)
        
