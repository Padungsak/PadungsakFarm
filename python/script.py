import webiopi
import datetime
import sys
import operator
sys.path.append('/home/pi/MyProject/python')
from engine import EngineImp
from valve import ValveImp
from sensor import SensorImp
from chemicalValve import ChemicalValveImp
from chemicalTank import ChemicalTankImp
from chemicalFeeder import ChemicalFeederImp
from mixingTank import MixingTankImp
from constantRate import ConstantRate
from chemicalOrderNum import ChemicalOrderNum
import threading

GPIO = webiopi.GPIO

g_valveDict = {}
g_sensorDict = {}
g_chemicalValveDict = {}
g_chemicalFeederDict = {}
g_chemicalTankDict = {}
g_mixingTank = 0
g_chemicalMessage = ''

g_stateList = {'Open':1,'Close':0, 'Auto':3, 'Error':4}
g_state = g_stateList['Close']

g_coconutState = g_stateList['Close']

g_chemicalStateList = {'Stop':0, 'Mixing':1, 'Pumping':2,'Pause':3, 'Error':-1}
g_chemicalState = g_chemicalStateList['Stop']
g_chemicalPauseEvent = threading.Event()

g_groundChemicalStateList = {'Stop':0, 'Pumping':1}
g_groundChemicalState = g_groundChemicalStateList['Stop']
g_groundChemicalStopEvent = threading.Event()

#s_mcp0 = webiopi.deviceInstance("mcp0")
#s_mcp0.setFunction(10, GPIO.IN)
# setup function is automatically called at WebIOPi startup
def setup():
    l_test = 1

# loop function is repeatedly called by WebIOPi 
def loop():
    #if s_mcp0.digitalRead(10) == GPIO.HIGH:
    #    webiopi.debug("1")
    #else:
    #    webiopi.debug("0")
    webiopi.sleep(1)

# destroy function is called at WebIOPi shutdown
def destroy():
    global g_valveDict
    g_valveDict.clear()
    global g_sensorDict
    g_sensorDict.clear()
    global g_chemicalValveDict
    g_chemicalValveDict.clear()
    global g_chemicalTankDict
    g_chemicalTankDict.clear()

#Add machine
@webiopi.macro
def InitialMachine(a_waterPumpGpioPort, a_chemicalPumpGpioPort, a_windPumpGpioPort, a_mixGpioPort, a_coconutWaterPumpPort):
    EngineImp.getInstance().Initialization(int(a_waterPumpGpioPort),
                                           int(a_chemicalPumpGpioPort),
                                           int(a_windPumpGpioPort),
                                           int(a_mixGpioPort),
                                           int(a_coconutWaterPumpPort))

#Add mixing tank
@webiopi.macro
def AddMixingTank(a_name, a_volumeGpioPort, a_maxVolumeGpioPort, a_waterValveGpioPort, a_drainValveGpioPort, a_rateTime, a_initialWater):
    global g_mixingTank
    if g_mixingTank == 0:
        g_mixingTank = MixingTankImp(a_name, int(a_volumeGpioPort), int(a_maxVolumeGpioPort), int(a_waterValveGpioPort), int(a_drainValveGpioPort), int(a_rateTime), int(a_initialWater))
    
#Add tank valve
@webiopi.macro
def AddChemicalTank(a_name, a_gpioSealedValve, a_chipNo, a_mcpMotorPort, a_mcpVolumePort, a_rateTime, a_isNC):
    global g_chemicalTankDict
    if(a_name not in g_chemicalTankDict):
        g_chemicalTankDict[a_name] = ChemicalTankImp(a_name, int(a_gpioSealedValve), int(a_chipNo), int(a_mcpMotorPort), int(a_mcpVolumePort), int(a_rateTime), int(a_isNC))

#Add chemical feeder
@webiopi.macro
def AddChemicalFeeder(a_name, a_chipNo, a_mcpMotorPort1, a_mcpMotorPort2, a_mcpMotorEnablePort, a_mcpShakePort, a_mcpShakeEnablePort, a_rateTime):
    global g_chemicalFeederDict
    if(a_name not in g_chemicalFeederDict):
        g_chemicalFeederDict[a_name] = ChemicalFeederImp(a_name, int(a_chipNo), int(a_mcpMotorPort1), int(a_mcpMotorPort2), int(a_mcpMotorEnablePort), int(a_mcpShakePort), int(a_mcpShakeEnablePort), int(a_rateTime))

		
#Add chemical valve
@webiopi.macro
def AddChemicalValve(a_name, a_chemicalPort, a_chemicalDelay, a_windPort, a_windDelay, a_executionOrder):
    global g_chemicalValveDict
    if(a_name not in g_chemicalValveDict):
        g_chemicalValveDict[a_name] = ChemicalValveImp(int(a_chemicalPort), int(a_chemicalDelay), int(a_windPort), int(a_windDelay), int(a_executionOrder))

#Add sensor macro
@webiopi.macro
def AddSensor(a_sensorName, a_analogPort):
    global g_sensorDict
    if(a_sensorName not in g_sensorDict):
        g_sensorDict[a_sensorName] = SensorImp(int(a_analogPort))

@webiopi.macro
def GetSensorValue(a_sensorName):
    # gives CPU some time before looping again
    return "%d" % g_sensorDict[a_sensorName].GetValue()
        
#Add valve macro
@webiopi.macro
def AddValve(a_valveName, a_valvePort, a_chemicalPort, a_executionOrder):
    global g_valveDict
    if(a_valveName not in g_valveDict):
        g_valveDict[a_valveName] = ValveImp(a_valveName, int(a_valvePort), int(a_chemicalPort), int(a_executionOrder))
    
#Open valve macro
@webiopi.macro
def OpenValve(a_valveName):
    #Open valve before start engine
    global g_state
    if(a_valveName in g_valveDict):
        g_valveDict[a_valveName].OpenValve()
        webiopi.sleep(0.5)
        EngineImp.getInstance().OpenWaterPump()
        g_state = g_stateList['Open']
        return g_valveDict[a_valveName].GetValveState()

    return ValveImp.m_valveStateList['Error']

#Close valve macro
@webiopi.macro
def CloseValve(a_valveName):
    #Short down engine before closing valve
    global g_state
    l_valveCount = 0
    for l_valveName, l_valveObj in g_valveDict.items():
        if(int(l_valveObj.GetValveState()) == ValveImp.m_valveStateList['Open']):
            l_valveCount = l_valveCount +1

    if(l_valveCount <= 1):
        EngineImp.getInstance().CloseWaterPump()
        g_state = g_stateList['Close']
    
    if(a_valveName in g_valveDict):
        g_valveDict[a_valveName].CloseValve()
        return g_valveDict[a_valveName].GetValveState()

    return ValveImp.m_valveStateList['Error']
        
@webiopi.macro
def GetValveState(a_valveName):
    if(a_valveName in g_valveDict):
        return "%d" % g_valveDict[a_valveName].GetValveState()

@webiopi.macro
def ExecutionAuto(a_delayTime, a_startOrder):
    #constRate = ConstantRate()
    #constRate.UpdateValue()
    ourThread = threading.Thread(target=DoExecutionAuto, args=[a_delayTime, a_startOrder])
    ourThread.start()
    
def DoExecutionAuto(a_delayTime, a_startOrder):
    global g_state
    g_state = g_stateList['Auto']
    
    for l_valveName, l_valveObj in g_valveDict.items():
        l_valveObj.CloseValve()
        webiopi.sleep(0.5)
        if(int(l_valveObj.GetValveState()) == ValveImp.m_valveStateList['Error']):
            EngineImp.getInstance().CloseWaterPump()
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
                    EngineImp.getInstance().CloseWaterPump()
                    g_state = g_stateList['Error']
                    return False
                l_isFound = True
        
        if(l_isFound):
            webiopi.debug('Auto mode found execution!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            l_previousOrderIndex = l_orderIndex - 1
            for l_valveName, l_valveObj in g_valveDict.items():
                if(l_valveObj.executionOrder == l_previousOrderIndex):
                    webiopi.sleep(30)
                    l_valveObj.CloseValve()
                    webiopi.sleep(0.5)
                    if(int(l_valveObj.GetValveState()) == ValveImp.m_valveStateList['Error']):
                        EngineImp.getInstance().CloseWaterPump()
                        g_state = g_stateList['Error']
                        return False
                    
            EngineImp.getInstance().OpenWaterPump()
            webiopi.sleep(int(a_delayTime))
        else:
            webiopi.debug('Auto mode not found execution!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            EngineImp.getInstance().CloseWaterPump()

            l_previousOrderIndex = l_orderIndex - 1
            for l_valveName, l_valveObj in g_valveDict.items():
                if(l_valveObj.executionOrder == l_previousOrderIndex):
                    l_valveObj.CloseValve()
                    webiopi.sleep(0.5)
            
            g_state = g_stateList['Close']
            return True

        l_orderIndex = l_orderIndex + 1

@webiopi.macro
def ExecutionCoconutWaterAuto(a_delayTime):
    ourThread = threading.Thread(target=DoExecutionCoconutWaterAuto, args=[a_delayTime])
    ourThread.start()

def DoExecutionCoconutWaterAuto(a_delayTime):
    global g_coconutState
    EngineImp.getInstance().OpenCoconutPump()
    g_coconutState = g_stateList['Auto']
    webiopi.sleep(int(a_delayTime))
    EngineImp.getInstance().CloseCoconutPump()
    g_coconutState = g_stateList['Close']
    return True

@webiopi.macro
def ExecutionChemicalAuto():
    global g_chemicalPauseEvent

    if VerifyChemicalInputData():
        ourThread = threading.Thread(target=DoChemicalAuto)
        g_chemicalPauseEvent.clear()
        ConstantRate.SaveToFile()
        ChemicalOrderNum.SaveToFile()
        ourThread.start()

def DoChemicalAuto():
    global g_chemicalState
    global g_chemicalPauseEvent
    
    l_sortedValve = sorted(g_chemicalValveDict.values(), key=operator.attrgetter('executionOrder'))
    
    #EngineImp.getInstance().OpenWindPump()
    for l_valve in l_sortedValve:
        if l_valve.IsValveClose() == True:
            #loop for openning all valve
            if g_mixingTank.IsWaterEnough() == False:
                g_chemicalState  = g_chemicalStateList['Mixing']
                if MixingTankProcessing() == False:
                    g_chemicalState  = g_chemicalStateList['Error']
                    break
            
            g_chemicalState = g_chemicalStateList['Pumping']

            #EngineImp.getInstance().OpenWindPump()
            #webiopi.sleep(l_valve.GetWindCompressDelayTime())
            g_mixingTank.CompressWind(l_valve.GetWindCompressDelayTime())
            l_valve.OpenValve()
            webiopi.sleep(3)

            EngineImp.getInstance().OpenChemicalPump()
            webiopi.sleep(l_valve.GetChemicalDelayTime())
            EngineImp.getInstance().CloseChemicalPump()
            webiopi.sleep(1)

            l_valve.OpenWindValve()
            webiopi.sleep(l_valve.GetWindDelayTime())
            l_valve.CloseValve()
            webiopi.sleep(1)
            l_valve.CloseWindValve()
            EngineImp.getInstance().CloseWindPump()
            webiopi.sleep(l_valve.GetSleepTime())

            while g_chemicalPauseEvent.is_set():
                ClearChemicalEngine()
                g_chemicalState = g_chemicalStateList['Pause']
                webiopi.debug('System pause')
                webiopi.sleep(5)
    
                    
    if g_chemicalState != g_chemicalStateList['Stop'] and g_chemicalState != g_chemicalStateList['Error']:
        #EngineImp.getInstance().CloseWindPump()
        g_mixingTank.CleanTank()
        g_chemicalState = g_chemicalStateList['Stop']
        ResetChemicalVolume()

@webiopi.macro
def ExecutionChemicalGroundAuto(a_startOrder):
    ourThread = threading.Thread(target=DoChemicalGroundAuto, args=[a_startOrder])
    ConstantRate.SaveToFile()
    ChemicalOrderNum.SaveToFile()
    ourThread.start()

def DoChemicalGroundAuto(a_startOrder):
    global g_groundChemicalState
    global g_groundChemicalStopEvent
    g_groundChemicalState = g_groundChemicalStateList['Pumping']
    
    #Use only one thank for all process
    if g_mixingTank.IsWaterEnough() == False:
        MixingTankProcessing()
    #######         
    
    for l_valveName, l_valveObj in g_valveDict.items():
        l_valveObj.CloseValve()
        webiopi.sleep(1)
        l_valveObj.CloseChemicalValve()
        webiopi.sleep(1)

    l_orderIndex = int(a_startOrder)

    l_isFound = True
    while l_isFound:
        l_isFound = False
        l_groundChemicalRate = 0
        l_groundChemicalRateTime = 0
        l_groundChemicalConstVolume = 0
        for l_valveName, l_valveObj in g_valveDict.items():
            if(l_valveObj.executionOrder == l_orderIndex):
                l_valveObj.OpenValve()
                webiopi.sleep(1)
                l_valveObj.OpenChemicalValve()
                webiopi.sleep(1)
                l_groundChemicalRate = float(l_valveObj.GetGroundChemicalRate())
                l_groundChemicalRateTime = l_valveObj.GetGroundChemicalRateTime()
                l_groundChemicalConstVolume = l_valveObj.GetChemicalConstVolume()
                l_isFound = True
                

        if l_isFound == True:
            l_groundChemicalCurrentVolume = 0
            while l_groundChemicalCurrentVolume < l_groundChemicalConstVolume:
                #if g_mixingTank.IsWaterEnough() == False:
                #  EngineImp.getInstance().CloseChemicalPump()
                #    webiopi.debug('EngineImp.getInstance().CloseChemicalPump()')
                #    webiopi.sleep(1)
                #    EngineImp.getInstance().CloseWaterPump()
                #    webiopi.debug('EngineImp.getInstance().CloseWaterPump()')
                #    webiopi.sleep(1)
                #    for l_valveName, l_valveObj in g_valveDict.items():
                #        if(l_valveObj.executionOrder == l_orderIndex):
                #            l_valveObj.CloseValve()
                #            webiopi.sleep(1)
                #            l_valveObj.CloseChemicalValve()
                #            webiopi.sleep(1)
                #    MixingTankProcessing()
                #    for l_valveName, l_valveObj in g_valveDict.items():
                #        if(l_valveObj.executionOrder == l_orderIndex):
                #            l_valveObj.OpenValve()
                #            webiopi.sleep(1)
                #            l_valveObj.OpenChemicalValve()
                #            webiopi.sleep(1)
                #else:
                
                #Put sleep delay. Just a workaround for heating on breaker.
                #EngineImp.getInstance().OpenMixPump()
                #webiopi.sleep(20)
                #EngineImp.getInstance().CloseMixPump()
                webiopi.sleep(120)
                #Put sleep for cool down breaker.
                #Do mixing chemical.Just a workaround for heating on breaker.
                EngineImp.getInstance().OpenMixPump()
                webiopi.sleep(60)
                EngineImp.getInstance().CloseMixPump()
                
                EngineImp.getInstance().OpenChemicalPump()
                webiopi.debug('EngineImp.getInstance().OpenChemicalPump()')
                webiopi.sleep(3)
                EngineImp.getInstance().OpenWaterPump()
                webiopi.debug('EngineImp.getInstance().OpenWaterPump()')
                webiopi.sleep(l_groundChemicalRateTime)
                #Close pump. Just a workaround for heating on breaker.
                EngineImp.getInstance().CloseChemicalPump()
                webiopi.debug('EngineImp.getInstance().CloseChemicalPump()')
                
                #add delay for clearing chemical in the pipe
                for l_valveName, l_valveObj in g_valveDict.items():
                    if(l_valveObj.executionOrder == l_orderIndex):
                        l_valveObj.CloseChemicalValve()
                        webiopi.sleep(1)
                webiopi.sleep(120)
                
                EngineImp.getInstance().CloseWaterPump()
                #####
                webiopi.debug('EngineImp.getInstance().CloseWaterPump()')
                l_groundChemicalCurrentVolume = l_groundChemicalCurrentVolume + l_groundChemicalRate
                webiopi.debug('l_groundChemicalCurrentVolume = %f' % l_groundChemicalCurrentVolume)

                if g_groundChemicalStopEvent.is_set():
                    g_groundChemicalStopEvent.clear()
                    g_groundChemicalState = g_groundChemicalStateList['Stop']
                    ClearGroundChemicalResource(a_startOrder)
                    return  True
                    
                    
            for l_valveName, l_valveObj in g_valveDict.items():
                if(l_valveObj.executionOrder == l_orderIndex):
                    EngineImp.getInstance().CloseChemicalPump()
                    webiopi.debug('EngineImp.getInstance().CloseChemicalPump()')
                    webiopi.sleep(1)
                    EngineImp.getInstance().CloseWaterPump()
                    webiopi.debug('EngineImp.getInstance().CloseWaterPump()')
                    webiopi.sleep(1)
                    l_valveObj.CloseValve()
                    webiopi.sleep(1)
                    l_valveObj.CloseChemicalValve()
                    webiopi.sleep(1)
                    
                    
        l_orderIndex = l_orderIndex + 1
    
    webiopi.debug('Exit DoChemicalGroundAuto()')
    EngineImp.getInstance().CloseMixPump()
    g_mixingTank.CleanTank()
    ResetChemicalVolume()
    g_groundChemicalState = g_groundChemicalStateList['Stop']
    return True

@webiopi.macro
def StopGroundChemical():
    global g_groundChemicalStopEvent
    g_groundChemicalStopEvent.set()
    

def ClearGroundChemicalResource(a_orderIndex):
    ClearChemicalEngine()
    l_orderIndex=int(a_orderIndex)
    l_isFound = True
    while l_isFound:
        l_isFound = False
        for l_valveName, l_valveObj in g_valveDict.items():
            if(l_valveObj.executionOrder == l_orderIndex):
                l_valveObj.CloseValve()
                webiopi.sleep(1)
                l_valveObj.CloseChemicalValve()
                webiopi.sleep(1)
                l_isFound = True
        l_orderIndex = l_orderIndex + 1

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
def IsCoconutAutoModeRunning():
    return (g_coconutState == g_stateList['Auto'])


@webiopi.macro
def StopWaterPump():
    global g_state
    EngineImp.getInstance().CloseWaterPump()
    if(g_state != g_stateList['Auto']):
        g_state = g_stateList['Close']

    
@webiopi.macro
def VerifyChemicalInputData():
    global g_chemicalMessage
    global g_chemicalState
    
    #Verify conditions used for fill chemical
    for l_tankObj in g_chemicalTankDict.values():
        l_chemicalInspectRet = l_tankObj.Inspection()
        if l_chemicalInspectRet == False:
            g_chemicalMessage = l_tankObj.GetErrorMessage()
            g_chemicalState = g_chemicalStateList['Error']
            return False

    for l_feederObj in g_chemicalFeederDict.values():
        l_chemicalInspectRet = l_feederObj.Inspection()
        if l_chemicalInspectRet == False:
            g_chemicalMessage = l_feederObj.GetErrorMessage()
            g_chemicalState = g_chemicalStateList['Error']
            return False
        
    l_waterInspectRet = g_mixingTank.Inspection()
    if l_waterInspectRet == False:
        g_chemicalMessage = g_mixingTank.GetErrorMessage()
        g_chemicalState = g_chemicalStateList['Error']
        return False
    return True

def MixingTankProcessing():
    #Check if chemical in tank is enough
    l_isChemicalEnough = False
    while l_isChemicalEnough == False:
        for l_tankIndex, l_tankKey in enumerate(g_chemicalTankDict):           
            if g_chemicalTankDict[l_tankKey].NeedToFillChemical():
                webiopi.debug('NeedToFillChemical %d!!' % l_tankIndex)
                l_isChemicalEnough = False
                webiopi.sleep(1)
                break
            else:
                l_isChemicalEnough = True
                
    g_mixingTank.InitialWater()
    if g_mixingTank.IsMixingTankError():
        return False

    l_sortedFeeder= sorted(g_chemicalFeederDict.values(), key=operator.attrgetter('m_orderNum'))
    for l_feederObj in l_sortedFeeder:
        EngineImp.getInstance().OpenMixPump()
        l_feederObj.FeedChemical()

    l_sortedTank= sorted(g_chemicalTankDict.values(), key=operator.attrgetter('m_orderNum'))              
    for l_tankObj in l_sortedTank:
        EngineImp.getInstance().OpenMixPump()
        l_tankObj.FillChemical()
        if g_mixingTank.IsMixingTankError():
            return False

    EngineImp.getInstance().CloseMixPump()
    #start motor for 10 min
    g_mixingTank.FillWater()
    if g_mixingTank.IsMixingTankError():
        return False

    return True

    
@webiopi.macro
def PauseChemical():
    global g_chemicalPauseEvent
    g_chemicalPauseEvent.set()

@webiopi.macro
def ContinueChemical():
    global g_chemicalPauseEvent
    g_chemicalPauseEvent.clear()

def ClearChemicalEngine():
    EngineImp.getInstance().CloseAllEngine()
    
    for l_valve in g_chemicalValveDict.values():
        l_valve.CloseValve()
        l_valve.CloseWindValve()
        webiopi.sleep(0.5)

    for l_tankObj in g_chemicalTankDict.values():
        l_tankObj.StopPump()
        webiopi.sleep(0.5)

    for l_feederObj in g_chemicalFeederDict.values():
        l_feederObj.StopFeeder()
        webiopi.sleep(0.5)

def ResetChemicalVolume():
    for l_tankObj in g_chemicalTankDict.values():
        l_tankObj.ResetChemicalVolume()

    for l_feederObj in g_chemicalFeederDict.values():
        l_feederObj.ResetChemicalVolume()
        
    g_mixingTank.ResetWaterVolume()
	
@webiopi.macro
def TestChemicalRate(a_name):
    if(a_name in g_chemicalTankDict):
        g_chemicalTankDict[a_name].TestFlowRate()
    elif(a_name in g_chemicalFeederDict):
        g_chemicalFeederDict[a_name].TestFeedRate()
        

@webiopi.macro
def TestWaterRate():
    g_mixingTank.TestFlowRate()

@webiopi.macro
def SetChemicalVolumeComponent(a_name, a_volume, a_constRate, a_order):
    if(a_name in g_chemicalTankDict):
        g_chemicalTankDict[a_name].SetChemicalVolume(float(a_volume))
        g_chemicalTankDict[a_name].SetChemicalConstRate(float(a_constRate), int(a_order))
    elif(a_name in g_chemicalFeederDict):
        g_chemicalFeederDict[a_name].SetChemicalVolume(float(a_volume))
        g_chemicalFeederDict[a_name].SetChemicalConstRate(float(a_constRate), int(a_order))

@webiopi.macro
def GetChemicalValumeComponent(a_name):
    if(a_name in g_chemicalTankDict):
        return g_chemicalTankDict[a_name].GetChemicalVolume()
    elif(a_name in g_chemicalFeederDict):
        return g_chemicalFeederDict[a_name].GetChemicalVolume()
    return "0,0,0"
        
@webiopi.macro
def SetWaterVolumeComponent(a_volume, a_constRate):
    g_mixingTank.SetWaterVolume(float(a_volume))
    g_mixingTank.SetWaterConstRate(float(a_constRate))

@webiopi.macro
def GetWaterVolumeComponent():
    return g_mixingTank.GetWaterVolume()

@webiopi.macro
def SetGroundChemicalVolumeComponent(a_name, a_volume):
    if(a_name in g_valveDict):
        g_valveDict[a_name].SetChemicalVolume(float(a_volume))

@webiopi.macro
def GetGroundChemicalVolumeComponent(a_name):
    if(a_name in g_valveDict):
        return g_valveDict[a_name].GetChemicalConstVolume()
    return "0"

@webiopi.macro
def IsChemicalInTankEnough(a_name):
    if(a_name in g_chemicalTankDict):
        return g_chemicalTankDict[a_name].IsChemicalInTankEnough()
    elif(a_name in g_chemicalFeederDict):
        return g_chemicalFeederDict[a_name].IsChemicalInTankEnough()
    return False

@webiopi.macro
def IsChemicalValveOpen(a_valveName):
    global g_chemicalValveDict
    if(a_valveName in g_chemicalValveDict):
        return g_chemicalValveDict[a_valveName].IsValveOpen()
    return False

@webiopi.macro
def IsChemicalValveDisable(a_valveName):
    global g_chemicalValveDict
    if(a_valveName in g_chemicalValveDict):
        return g_chemicalValveDict[a_valveName].IsValveDisable()
    return False

@webiopi.macro
def IsChemicalValveClose(a_valveName):
    global g_chemicalValveDict
    if(a_valveName in g_chemicalValveDict):
        return g_chemicalValveDict[a_valveName].IsValveClose()
    return False
	
@webiopi.macro
def SetchemicalValveDisable(a_valveName):
    global g_chemicalValveDict
    if(a_valveName in g_chemicalValveDict):
        g_chemicalValveDict[a_valveName].SetDisableValve()
		
@webiopi.macro
def SetchemicalValveNormal(a_valveName):
    global g_chemicalValveDict
    if(a_valveName in g_chemicalValveDict):
        g_chemicalValveDict[a_valveName].SetNormalValve()
	
@webiopi.macro
def IsChemicalModeError():
    return (g_chemicalState == g_chemicalStateList['Error'])
	
@webiopi.macro
def IsChemicalModeStop():
    return (g_chemicalState == g_chemicalStateList['Stop'])

@webiopi.macro
def IsChemicalModePumping():
    return (g_chemicalState == g_chemicalStateList['Pumping'])

@webiopi.macro
def IsChemicalModeMixing():
    print("IsChemicalModeMixing!!!! %d" % (g_chemicalState))
    return (g_chemicalState == g_chemicalStateList['Mixing'])

@webiopi.macro
def IsChemicalModePause():
    print("IsChemicalModePause!!!! %d" % (g_chemicalState))
    return (g_chemicalState == g_chemicalStateList['Pause'])

@webiopi.macro
def GetChemicalMessage():
    return g_chemicalMessage

@webiopi.macro
def IsGroundChemicalRunning():
    return (g_groundChemicalState == g_groundChemicalStateList['Pumping'])

@webiopi.macro
def IsGroundChemicalStop():
    return (g_groundChemicalState == g_groundChemicalStateList['Stop'])
    
