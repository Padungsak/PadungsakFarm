import webiopi
import os.path

class ChemicalOrderNum:
    s_fileName = "ChemicalOrderNumber.txt"
    s_splitter = "="
    s_orderDict = {}
    
    def __init__(self):
        if not ChemicalOrderNum.s_orderDict:
            if (os.path.isfile(ChemicalOrderNum.s_fileName)):
                l_file = open(ChemicalOrderNum.s_fileName, "r")
                for l_line in l_file:
                    l_splitted = l_line.split(ChemicalOrderNum.s_splitter)
                    if(len(l_splitted) == 2):
                        ChemicalOrderNum.s_orderDict[l_splitted[0]] = int(l_splitted[1])
                l_file.close()

    def UpdateOrder(self, a_name, a_value):
        ChemicalOrderNum.s_orderDict[a_name] = a_value
        webiopi.debug('UpdateChemicalOrder @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s' % a_name)
        webiopi.debug('UpdateChemicalOrder @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %d' % a_value)

    @staticmethod
    def GetOrder(a_name):
        for l_name, l_value in ChemicalOrderNum.s_orderDict.items():
            if (l_name == a_name):
                webiopi.debug('GetChemicalOrder @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %d' % l_value)
                return l_value
        return 0

    @staticmethod
    def SaveToFile():
        l_file = open(ChemicalOrderNum.s_fileName, "w")
        for l_name, l_value in ChemicalOrderNum.s_orderDict.items():
            l_file.write(l_name + ChemicalOrderNum.s_splitter + str(l_value) + "\n")
        l_file.close()
        
