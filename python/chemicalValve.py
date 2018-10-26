import webiopi
GPIO = webiopi.GPIO

class ChemicalValveImp:
    s_mcp1 = webiopi.deviceInstance("mcp2")
    s_windCompressDelay = 780
    s_sleepModeDelay = 180
    s_valveStateList = {'Open':1,'Close':0,'Error':-1}
    
    def __init__(self, a_chemicalPortNum, a_chemicalDelay, a_windPortNum, a_windDelay, a_executionOrder):
        self.m_chemicalPortNum = a_chemicalPortNum
        self.m_chemicalDelay = a_chemicalDelay
        self.m_windPortNum = a_windPortNum
        self.m_windDelay = a_windDelay
        self.executionOrder = a_executionOrder
        self.m_valveState = ChemicalValveImp.s_valveStateList['Close']
        ChemicalValveImp.s_mcp1.setFunction(self.m_chemicalPortNum, GPIO.OUT)
        ChemicalValveImp.s_mcp1.setFunction(self.m_windPortNum, GPIO.OUT)
        ChemicalValveImp.s_mcp1.digitalWrite(self.m_chemicalPortNum, GPIO.HIGH)
        ChemicalValveImp.s_mcp1.digitalWrite(self.m_windPortNum, GPIO.HIGH)
        
		
    def IsValveOpen(self):
        return self.m_valveState == ChemicalValveImp.s_valveStateList['Open']

    def IsValveClose(self):
        return self.m_valveState == ChemicalValveImp.s_valveStateList['Close']

    def IsValveError(self):
        return self.m_valveState == ChemicalValveImp.s_valveStateList['Error']

    def OpenValve(self):
        ChemicalValveImp.s_mcp1.digitalWrite(self.m_chemicalPortNum, GPIO.LOW)
        self.m_valveState = ChemicalValveImp.s_valveStateList['Open']
        webiopi.debug('Open valve port %d' % self.m_chemicalPortNum)
	
    def CloseValve(self):
        ChemicalValveImp.s_mcp1.digitalWrite(self.m_chemicalPortNum, GPIO.HIGH)
        self.m_valveState = ChemicalValveImp.s_valveStateList['Close']
        webiopi.debug('Close valve port %d' % self.m_chemicalPortNum)


    def OpenWindValve(self):
        ChemicalValveImp.s_mcp1.digitalWrite(self.m_windPortNum, GPIO.LOW)
        self.m_valveState = ChemicalValveImp.s_valveStateList['Open']
        webiopi.debug('Open wind valve port %d' % self.m_windPortNum)
    
    def CloseWindValve(self):
        ChemicalValveImp.s_mcp1.digitalWrite(self.m_windPortNum, GPIO.HIGH)
        self.m_valveState = ChemicalValveImp.s_valveStateList['Close']
        webiopi.debug('Close wind valve port %d' % self.m_windPortNum)

    def GetWindDelayTime(self):
        return self.m_windDelay

    def GetChemicalDelayTime(self):
        return self.m_chemicalDelay

    def GetWindCompressDelayTime(self):
        return ChemicalValveImp.s_windCompressDelay

    def GetSleepTime(self):
        return ChemicalValveImp.s_sleepModeDelay
