import webiopi
import datetime
import sys
sys.path.append('/home/pi/MyProject/python')
from valve import ValveImp
from sensor import SensorImp
import threading

GPIO = webiopi.GPIO

g_valveDict = {}
g_sensorDict = {}

g_stateList = {'Open':1,'Close':0, 'Auto':3, 'Error':4}
g_state = g_stateList['Close']

# setup function is automatically called at WebIOPi startup
def setup():
    l_test = 1

# loop function is repeatedly called by WebIOPi 
def loop():
    # gives CPU some time before looping again
    webiopi.sleep(0.5)

# destroy function is called at WebIOPi shutdown
def destroy():
    global g_valveDict
    g_valveDict.clear()
    GPIO.digitalWrite(LIGHT, GPIO.LOW)

#Add sensor macro
@webiopi.macro
def AddSensor(a_sensorName, a_analogPort):
    global g_sensorDict
    if(a_sensorName not in g_sensorDict):
        g_sensorDict[a_sensorName] = SensorImp(int(a_analogPort))

@webiopi.macro
def GetSensorValue(a_sensorName):
    return "%d" % g_sensorDict[a_sensorName].GetValue()
        
#Add valve macro
@webiopi.macro
def AddValve(a_valveName, a_relayPort1, a_relayPort2, a_executionOrder):
    global g_valveDict
    if(a_valveName not in g_valveDict):
        g_valveDict[a_valveName] = ValveImp(int(a_relayPort1),int(a_relayPort2), a_executionOrder)
    
#Open valve macro
@webiopi.macro
def OpenValve(a_valveName):
    #Open valve before start engine
    l_valveState = ValveImp.m_valveStateList['Close']
    if(a_valveName in g_valveDict):
        g_valveDict[a_valveName].OpenValve()
        l_valveState = g_valveDict[a_valveName].GetValveState()

        if(l_valveState == ValveImp.m_valveStateList['Open']):
            l_valveCount = 0
            for l_valveName, l_valveObj in g_valveDict.items():
                if(int(l_valveObj.GetValveState()) == ValveImp.m_valveStateList['Open']):
                    l_valveCount = l_valveCount +1
                    
            if(l_valveCount >= 2):
                StartMachine(2)
                
    return l_valveState

#Close valve macro
@webiopi.macro
def CloseValve(a_valveName):
    #Short down engine before closing valve
    l_valveCount = 0
    for l_valveName, l_valveObj in g_valveDict.items():
        if(int(l_valveObj.GetValveState()) == ValveImp.m_valveStateList['Open']):
            l_valveCount = l_valveCount +1

    if(l_valveCount <= 2):
        StopMachine(2)
        
    l_valveState = ValveImp.m_valveStateList['Open']
    if(a_valveName in g_valveDict):
        g_valveDict[a_valveName].CloseValve()
        l_valveState = g_valveDict[a_valveName].GetValveState()

    return l_valveState

@webiopi.macro
def GetValveState(a_valveName):
    if(a_valveName in g_valveDict):
        return "%d" % g_valveDict[a_valveName].GetValveState()

def DoExecutionAuto(a_delayTime, a_startOrder, a_machinePort):
    global g_state
    g_state = g_stateList['Auto']
    
    for l_valveName, l_valveObj in g_valveDict.items():
        l_valveObj.CloseValve()
        webiopi.sleep(0.5)
        if(int(l_valveObj.GetValveState()) == ValveImp.m_valveStateList['Error']):
                    StopMachine(a_machinePort)
                    g_state = g_stateList['Error']
                    return False
                
    l_orderIndex = int(a_startOrder)
    l_isFound = True
    while l_isFound:
        l_isFound = False
        for l_valveName, l_valveObj in g_valveDict.items():
            if(l_valveObj.executionOrder == l_orderIndex):
                l_valveObj.OpenValve()
                webiopi.sleep(0.5)
                if(int(l_valveObj.GetValveState()) == ValveImp.m_valveStateList['Error']):
                    StopMachine(a_machinePort)
                    g_state = g_stateList['Error']
                    return False
                l_isFound = True
        
        if(l_isFound):
            webiopi.debug('Auto mode found execution!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            l_previousOrderIndex = l_orderIndex - 1
            for l_valveName, l_valveObj in g_valveDict.items():
                if(l_valveObj.executionOrder == l_previousOrderIndex):
                    l_valveObj.CloseValve()
                    webiopi.sleep(0.5)
                    if(int(l_valveObj.GetValveState()) == ValveImp.m_valveStateList['Error']):
                        StopMachine(a_machinePort)
                        g_state = g_stateList['Error']
                        return False
                    
            StartMachine(a_machinePort)
            webiopi.sleep(int(a_delayTime))
        else:
            webiopi.debug('Auto mode not found execution!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            StopMachine(a_machinePort)
            g_state = g_stateList['Close']
            return True

        l_orderIndex = l_orderIndex + 1
    
@webiopi.macro
def ExecutionAuto(a_delayTime, a_startOrder, a_machinePort):
    ourThread = threading.Thread(target=DoExecutionAuto, args=[a_delayTime, a_startOrder, a_machinePort])
    ourThread.start()

@webiopi.macro
def IsAutoModeRunning():
    return (g_state == g_stateList['Auto'])

@webiopi.macro
def IsMachineOpennig():
    return (g_state == g_stateList['Open'])

@webiopi.macro
def IsMachineClosing():
    return (g_state == g_stateList['Close'])

@webiopi.macro
def IsAutoModeError():
    return (g_state == g_stateList['Error'])

@webiopi.macro
def StartMachine(a_relayPort):
    global g_state
    relayPortConverted = int(a_relayPort)
    GPIO.setFunction(relayPortConverted, GPIO.OUT)
    GPIO.digitalWrite(relayPortConverted, GPIO.LOW)
    if(g_state != g_stateList['Auto']):
        g_state = g_stateList['Open']

@webiopi.macro
def StopMachine(a_relayPort):
    global g_state
    relayPortConverted = int(a_relayPort)
    GPIO.setFunction(relayPortConverted, GPIO.OUT)
    GPIO.digitalWrite(relayPortConverted, GPIO.HIGH)
    if(g_state != g_stateList['Auto']):
        g_state = g_stateList['Close']
    


           
        
    
