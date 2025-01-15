import webiopi
GPIO = webiopi.GPIO

class ChemicalValveImp:
    #s_mcp1 = webiopi.deviceInstance("mcp2")
    s_sleepModeDelay = 30
    s_valveStateList = {'Open':1,'Normal':0,'Disable':-1}
    
    def __init__(self, a_chipNo, a_chemicalPortNum, a_chemicalDelay, a_windGpioPortNum, a_windDelay, a_executionOrder):
        self.m_mcp = webiopi.deviceInstance("mcp%d" % a_chipNo)
        self.m_chemicalPortNum = a_chemicalPortNum
        self.m_chemicalDelay = a_chemicalDelay
        self.m_windGpioPortNum = a_windGpioPortNum
        self.m_windDelay = a_windDelay
        self.executionOrder = a_executionOrder
        self.m_valveState = ChemicalValveImp.s_valveStateList['Disable']
        
        self.m_mcp.setFunction(self.m_chemicalPortNum, GPIO.OUT)
        GPIO.setFunction(self.m_windGpioPortNum, GPIO.OUT)
        self.m_mcp.digitalWrite(self.m_chemicalPortNum, GPIO.HIGH)
        GPIO.digitalWrite(self.m_windGpioPortNum, GPIO.HIGH)
        
		
    def IsValveOpen(self):
        return self.m_valveState == ChemicalValveImp.s_valveStateList['Open']

    def IsValveClose(self):
        return self.m_valveState == ChemicalValveImp.s_valveStateList['Normal']

    def IsValveDisable(self):
        return self.m_valveState == ChemicalValveImp.s_valveStateList['Disable']

    def OpenValve(self):
        if self.m_valveState != ChemicalValveImp.s_valveStateList['Disable']:
            self.m_mcp.digitalWrite(self.m_chemicalPortNum, GPIO.LOW)
            self.m_valveState = ChemicalValveImp.s_valveStateList['Open']
            webiopi.debug('Open valve port %d' % self.m_chemicalPortNum)
	
    def CloseValve(self):
        if self.m_valveState != ChemicalValveImp.s_valveStateList['Disable']:
            self.m_mcp.digitalWrite(self.m_chemicalPortNum, GPIO.HIGH)
            self.m_valveState = ChemicalValveImp.s_valveStateList['Normal']
            webiopi.debug('Close valve port %d' % self.m_chemicalPortNum)


    def OpenWindValve(self):
        GPIO.digitalWrite(self.m_windGpioPortNum, GPIO.LOW)
        webiopi.debug('Open wind valve port %d' % self.m_windGpioPortNum)
    
    def CloseWindValve(self):
        GPIO.digitalWrite(self.m_windGpioPortNum, GPIO.HIGH)
        webiopi.debug('Close wind valve port %d' % self.m_windGpioPortNum)
            

    def GetWindDelayTime(self):
        return self.m_windDelay

    def GetChemicalDelayTime(self):
        return self.m_chemicalDelay

    def GetSleepTime(self):
        return ChemicalValveImp.s_sleepModeDelay

    def SetDisableValve(self):
        webiopi.debug('SetDisableValve %d' %self.m_chemicalPortNum )
        self.m_valveState = ChemicalValveImp.s_valveStateList['Disable']

    def SetNormalValve(self):
        self.m_valveState = ChemicalValveImp.s_valveStateList['Normal']
