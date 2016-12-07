import regCtrl,os

regOrig = regCtrl.read("00000004")
regBin = format(int(regOrig,16),"032b")
regBinList = list(regBin)
regBinList[len(regBinList)-12] = '1'
regBin = "".join(regBinList)
regReset = format(int(regBin,10),"08X")
regCtrl.write("00000004",regReset)
regCtrl.write("00000004",'0000020C')
