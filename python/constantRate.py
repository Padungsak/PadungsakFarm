import webiopi
import os.path

class ConstantRate:
    s_fileName = "ConstantRate.txt"
    s_splitter = "="
    s_constDict = {}
    
    def __init__(self):
        if not ConstantRate.s_constDict:
            if (os.path.isfile(ConstantRate.s_fileName)):
                l_file = open(ConstantRate.s_fileName, "r")
                for l_line in l_file:
                    l_splitted = l_line.split(ConstantRate.s_splitter)
                    if(len(l_splitted) == 2):
                        ConstantRate.s_constDict[l_splitted[0]] = float(l_splitted[1])
                l_file.close()

    def UpdateRate(self, a_rateName, a_value):
        ConstantRate.s_constDict[a_rateName] = a_value
        webiopi.debug('UpdateRate @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s' % a_rateName)
        webiopi.debug('UpdateRate @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %d' % a_value)

    @staticmethod
    def GetRate(a_rateName):
        for l_name, l_value in ConstantRate.s_constDict.items():
            if (l_name == a_rateName):
                webiopi.debug('GetRate @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %f' % l_value)
                return l_value
        return 0

    @staticmethod
    def SaveToFile():
        l_file = open(ConstantRate.s_fileName, "w")
        for l_name, l_value in ConstantRate.s_constDict.items():
            l_file.write(l_name + ConstantRate.s_splitter + str(l_value) + "\n")
        l_file.close()
        
