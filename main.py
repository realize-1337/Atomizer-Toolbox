import os
import math
import subprocess
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
import packages.dimLess as dL
from packages.calculator import Calculator as ca
from pyfluids import Fluid, FluidsList, Input
UI_FILE = './GUI/mainWindow.ui'
PY_FILE = './GUI/mainWindow.py'
subprocess.run(['pyuic6', '-x', UI_FILE, '-o', PY_FILE])
from GUI.mainWindow import Ui_MainWindow as main



class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = main()
        self.ui.setupUi(self)
        self.resutlLabels = self.createLabelList()
        self.setCalcButtons()
        self.ui.pushButton.clicked.connect(self.readValues)
        self.tabOrder()

    def tabOrder(self):
        order = [self.ui.innerTube, self.ui.innerWall, self.ui.annularSheet, self.ui.middleWall, self.ui.outerSheet, self.ui.liquidTemp, self.ui.calcLiq, self.ui.gasTemp, self.ui.calcGas, self.ui.innerStreamValue, self.ui.sheetStreamValue, self.ui.outerStreamValue, self.ui.pushButton]
        self.setTabOrder(order[0], order[1])
        for i in range(1, len(order)):
            self.setTabOrder(order[i-1], order[i])
        
        #self.setTabOrder(order[-1], order[0])

    def setCalcButtons(self):
        self.ui.calcGas.clicked.connect(self.calcGas)
        self.ui.calcLiq.clicked.connect(self.calcLiq)

        self.calcLiq()
        self.calcGas()
        
    def enableAutoCalc(self):
        self.ui.liquidTemp.valueChanged.connect(self.calcLiq)
        self.ui.liquidVisc.valueChanged.connect(self.calcLiqDens)
        self.ui.gasTemp.valueChanged.connect(self.calcGas)

    def calcLiq(self):
        
        if self.ui.liquidType.currentText() == 'Water':
            water_ = Fluid(FluidsList.Water).with_state(Input.temperature(self.ui.liquidTemp.value()), Input.pressure(101325))
            self.ui.liquidVisc.setValue(water_.dynamic_viscosity*1000)
            self.ui.LiquidDens.setValue(water_.density)
            self.liqSurface = water_ST = 235.8e-3*((water_.critical_temperature-self.ui.liquidTemp.value())/(water_.critical_temperature+273.15))**1.256*(1-0.625*((water_.critical_temperature-self.ui.liquidTemp.value())/(water_.critical_temperature+273.15)))
        else: 
            try: glycerinFraction = ca(self.ui.liquidTemp.value(), self.ui.liquidVisc.value()).solve()
            except: glycerinFraction = 0
            rhoGly = ca(self.ui.liquidTemp.value(), self.ui.liquidVisc.value()).rhoGlycerin()
            water_ = Fluid(FluidsList.Water).with_state(Input.temperature(self.ui.liquidTemp.value()), Input.pressure(101325))
            rhoMix = rhoGly*glycerinFraction + water_.density*(1-glycerinFraction)
            self.ui.LiquidDens.setValue(rhoMix)
            surfaceGly = 0.06*self.ui.liquidTemp.value()+64.6
            surfaceGly /= 1000
            water_ST = 235.8e-3*((water_.critical_temperature-self.ui.liquidTemp.value())/(water_.critical_temperature+273.15))**1.256*(1-0.625*((water_.critical_temperature-self.ui.liquidTemp.value())/(water_.critical_temperature+273.15)))
            surfaceMix = glycerinFraction*surfaceGly + (1-glycerinFraction)*water_ST
            self.liqSurface = surfaceMix
        
    def calcGas(self):
        try:
            if self.ui.gasType.currentText() == 'Air':
                air_ = Fluid(FluidsList.Air).with_state(Input.temperature(self.ui.gasTemp.value()), Input.pressure(101325))
                self.ui.gasVisc.setValue(air_.dynamic_viscosity*1000)
                print(air_.dynamic_viscosity*1000)
                self.ui.gasDens.setValue(air_.density)
                self.gasSurface = air_.surface_tension
        except: pass

    def createLabelList(self):
        resutlLabels = []
        resutlLabels.append(self.ui.innerMFR)
        resutlLabels.append(self.ui.sheetMFR)
        resutlLabels.append(self.ui.outerMFR)

        resutlLabels.append(self.ui.innerVel)
        resutlLabels.append(self.ui.sheetVel)
        resutlLabels.append(self.ui.outerVel)

        resutlLabels.append(self.ui.innerMom_flux)
        resutlLabels.append(self.ui.sheetMom_flux)
        resutlLabels.append(self.ui.outerMom_flux)

        resutlLabels.append(self.ui.innerMom)
        resutlLabels.append(self.ui.sheetMom)
        resutlLabels.append(self.ui.outerMom)
        

        resutlLabels.append(self.ui.innerRe)
        resutlLabels.append(self.ui.innerWe)
        resutlLabels.append(self.ui.innerOh)

        resutlLabels.append(self.ui.sheetRe)
        resutlLabels.append(self.ui.sheetWe)
        resutlLabels.append(self.ui.outerOh)
    
        resutlLabels.append(self.ui.outerRe)
        resutlLabels.append(self.ui.outerWe)
        resutlLabels.append(self.ui.sheetOh)
        

        resutlLabels.append(self.ui.totalGLR)
        resutlLabels.append(self.ui.totalMom)
        resutlLabels.append(self.ui.innerSheetGLR)
        resutlLabels.append(self.ui.outerSheetGLR)
        resutlLabels.append(self.ui.innerSheetMom)
        resutlLabels.append(self.ui.outerSheetMom)

        for label in resutlLabels:
            label.setText('-')
        return resutlLabels

    def readValues(self):
        self.calcLiq()
        self.calcGas()
        # Atomizer Geometry
        self.Lc = []
        self.innerTube = self.ui.innerTube.value()/1000
        self.Lc.append(self.innerTube)
        self.innerWall = self.ui.innerWall.value()/1000
        self.annularSheet = self.ui.annularSheet.value()/1000
        self.Lc.append(self.annularSheet)
        self.middleWall = self.ui.middleWall.value()/1000
        self.outerSheet = self.ui.outerSheet.value()/1000
        self.Lc.append(self.outerSheet)
        self.outerWall = self.ui.outerWall.value()/1000
        self.orifice()

        # Fluid Properties
        ## Liquid
        self.liqType = self.ui.liquidType.currentText()
        self.liqTemp = self.ui.liquidTemp.value()+273.15
        self.liqVisc = self.ui.liquidVisc.value()/1000
        self.liqDens = self.ui.LiquidDens.value()

        ## Gas
        self.gasType = self.ui.gasType.currentText()
        self.gasTemp = self.ui.gasTemp.value()+275.15
        self.gasVisc = self.ui.gasVisc.value()/1000
        self.gasDens = self.ui.gasDens.value()

        # Stream Properties
        # values are converted to kg/s
        self.streams = []
        value = self.ui.innerStreamValue.value()
        unit = self.ui.innerStreamUnit.currentText()
        if self.ui.innerGasTrue.isChecked():
            type = 'gas'
        else: type = 'liquid'
        self.streams.append([value, unit, type])

        value = self.ui.sheetStreamValue.value()
        unit = self.ui.sheetStreamUnit.currentText()
        if self.ui.sheetGasTrue.isChecked():
            type = 'gas'
        else: type = 'liquid'
        self.streams.append([value, unit, type])

        value = self.ui.outerStreamValue.value()
        unit = self.ui.outerStreamUnit.currentText()
        if self.ui.outerGasTrue.isChecked():
            type = 'gas'
        else: type = 'liquid'
        self.streams.append([value, unit, type])

        self.streamValues = []
        def velCalc(mfr, orifice, type):
            mfr_h = mfr*3600
            if type == 'gas':
                dens = self.gasDens 
            else: dens = self.liqDens
            vel = mfr/dens/orifice
            mom = dens*vel**2*orifice
            mom_flux = dens*vel**2
            print(orifice)
            return [mfr, mfr_h, vel, mom_flux, mom, type]

        i = 0
        for item in self.streams:
            area = self.orificeDict[i]
            i += 1
            value, unit, type = item
            if unit == 'kg/h':
                item[0] /= 3600
            elif unit == 'g/s':
                item[0] /= 1000
            elif unit == 'm/s':
                item[0] *= area
                if type == 'gas':
                    item[0] *= self.gasDens
                else:
                    item[0] *= self.liqDens 

            self.streamValues.append(velCalc(item[0], area, type))

        self.fillFirstResults()

    def orifice(self):
        self.innerArea = math.pi/4*self.innerTube**2
        self.innerAreaWithWall = math.pi*(self.innerTube/2+self.innerWall)**2

        liquidSheetRadius = self.innerTube/2 + self.annularSheet + self.innerWall
        self.liquidArea = math.pi*liquidSheetRadius**2 - self.innerAreaWithWall
        self.liquidAreaWithWall = math.pi*(liquidSheetRadius+self.middleWall)**2 - self.innerAreaWithWall

        outerSheetRadius = liquidSheetRadius + self.middleWall + self.outerSheet
        self.outerArea = math.pi*outerSheetRadius**2 - self.liquidAreaWithWall - self.innerAreaWithWall
        self.orificeDict = {
            0: self.innerArea,
            1: self.liquidArea,
            2: self.outerArea
        }

    def fillFirstResults(self):
        streamValuesString = [[0]*5 for i in range(3)]
        for j in range(len(self.streamValues[0])-1):
            for i in range(3):
                if self.streamValues[i][j] < 0.001:
                    streamValuesString[i][j] = "%.3e" % self.streamValues[i][j]
                else: 
                    streamValuesString[i][j] = "%.3f" % self.streamValues[i][j]
            

        self.resutlLabels[0].setText(streamValuesString[0][1])
        self.resutlLabels[1].setText(streamValuesString[1][1])
        self.resutlLabels[2].setText(streamValuesString[2][1])

        self.resutlLabels[3].setText(streamValuesString[0][2])
        self.resutlLabels[4].setText(streamValuesString[1][2])
        self.resutlLabels[5].setText(streamValuesString[2][2])
        
        self.resutlLabels[6].setText(streamValuesString[0][3])
        self.resutlLabels[7].setText(streamValuesString[1][3])
        self.resutlLabels[8].setText(streamValuesString[2][3])
        
        self.resutlLabels[9].setText(streamValuesString[0][4])
        self.resutlLabels[10].setText(streamValuesString[1][4])
        self.resutlLabels[11].setText(streamValuesString[2][4])

        self.calcDimless()

    def calcDimless(self):
        # Re, We, Oh

        rhos = {
            'gas': self.gasDens,
            'liquid': self.liqDens
        }
        visc = {
            'gas': self.gasVisc,
            'liquid': self.liqVisc
        }
        sigmas = {
            'gas': self.liqSurface,
            'liquid': self.liqSurface
        }
        
        self.innerDimless = []
        self.sheetDimless = []
        self.outerDimless = []

        self.innerDimless.append(dL.Re(self.streamValues[0][2], rhos[self.streamValues[0][5]], self.Lc[0], visc[self.streamValues[0][5]]))
        self.sheetDimless.append(dL.Re(self.streamValues[1][2], rhos[self.streamValues[1][5]], self.Lc[1], visc[self.streamValues[1][5]]))
        self.outerDimless.append(dL.Re(self.streamValues[2][2], rhos[self.streamValues[2][5]], self.Lc[2], visc[self.streamValues[2][5]]))
        
        self.innerDimless.append(dL.We(self.streamValues[0][2], rhos[self.streamValues[0][5]], self.Lc[0], sigmas[self.streamValues[0][5]]))
        self.sheetDimless.append(dL.We(self.streamValues[1][2], rhos[self.streamValues[1][5]], self.Lc[1], sigmas[self.streamValues[1][5]]))
        self.outerDimless.append(dL.We(self.streamValues[2][2], rhos[self.streamValues[2][5]], self.Lc[2], sigmas[self.streamValues[2][5]]))
        
        self.innerDimless.append(dL.Oh(visc[self.streamValues[0][5]], rhos[self.streamValues[0][5]], self.Lc[0], sigmas[self.streamValues[0][5]]))
        self.sheetDimless.append(dL.Oh(visc[self.streamValues[1][5]], rhos[self.streamValues[1][5]], self.Lc[1], sigmas[self.streamValues[1][5]]))
        self.outerDimless.append(dL.Oh(visc[self.streamValues[2][5]], rhos[self.streamValues[2][5]], self.Lc[2], sigmas[self.streamValues[2][5]]))

        print(self.innerDimless)
        print(self.sheetDimless)
        print(self.outerDimless)

        strings = []
        for item in self.innerDimless:
            if item < 0.01 or item > 1000:
                strings.append("%.2e" % item)
            else: 
                strings.append("%.2f" % item)
        
        for item in self.sheetDimless:
            if item < 0.01 or item > 1000:
                strings.append("%.2e" % item)
            else: 
                strings.append("%.2f" % item)
        
        for item in self.outerDimless:
            if item < 0.01 or item > 1000:
                strings.append("%.2e" % item)
            else: 
                strings.append("%.2f" % item)


        for i in range(len(strings)):
            self.resutlLabels[12+i].setText(strings[i])

        # GLR 

        gasMF = 0
        liqMF = 0
        gasMom_flux = 0
        liqMom_flux = 0
        
        for i in range(3):
            if self.streamValues[i][-1] == 'gas':
                gasMF += self.streamValues[i][0]
                gasMom_flux += self.streamValues[i][3]
            elif self.streamValues[i][-1] == 'liquid':
                liqMF += self.streamValues[i][0]
                liqMom_flux += self.streamValues[i][3]
        
        if liqMF != 0 and liqMom_flux != 0:
            self.GLR_total = gasMF/liqMF
            self.mom_flux_total = gasMom_flux/liqMom_flux
            if self.streamValues[0][-1] == 'gas' and self.streamValues[1][-1] == 'liquid' and self.streamValues[2][-1] == 'gas':
                self.GLI = self.streamValues[0][0]/self.streamValues[1][0]
                self.GLO = self.streamValues[2][0]/self.streamValues[1][0]
                self.mom_i = self.streamValues[0][3]/self.streamValues[1][3]
                self.mom_o = self.streamValues[2][3]/self.streamValues[1][3]
            else: 
                self.GLI = 0
                self.GLO = 0
                self.mom_i = 0
                self.mom_o = 0
            

            self.resutlLabels[21].setText("%.2f" % self.GLR_total)
            self.resutlLabels[22].setText("%.2f" % self.mom_flux_total)
            self.resutlLabels[23].setText("%.2f" % self.GLI)
            self.resutlLabels[24].setText("%.2f" % self.GLO)
            self.resutlLabels[25].setText("%.2f" % self.mom_i)
            self.resutlLabels[26].setText("%.2f" % self.mom_o)
        
        else:
            self.resutlLabels[21].setText('Error')
            self.resutlLabels[22].setText('Error')
            self.resutlLabels[23].setText('Error')
            self.resutlLabels[24].setText('Error')
            self.resutlLabels[25].setText('Error')
            self.resutlLabels[26].setText('Error')

       


        
if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    window = UI()
    window.show()
    app.exec()