from PyQt5 import QtWidgets, uic, QtCore
import sys
import os
import screen_brightness_control as sbc
if os.name == 'nt':
    import keyboard

#Check if --lodpi was an arguement, if not use HiDPI
if len(sys.argv) == 2 and sys.argv[1] == '--lodpi':
    print("Using Low DPI mode")
else:
    #thanks https://leomoon.com/journal/python/high-dpi-scaling-in-pyqt5/
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

    print("Using HiDPI mode")

class Ui(QtWidgets.QMainWindow):
    
    #Pull in all of the interface elements so I can interact with them
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('exp.ui', self)
        self.dial = self.findChild(QtWidgets.QDial, 'dialMins')
        self.dial.valueChanged.connect(self.sliderMoved)
        self.dial.setValue(90)
        self.dial.setMaximum(180)
        self.btnStart = self.findChild(QtWidgets.QPushButton, 'btnStart')
        self.btnUp = self.findChild(QtWidgets.QPushButton, 'btnUp')
        self.btnDown = self.findChild(QtWidgets.QPushButton, 'btnDown')
        self.spnTime = self.findChild(QtWidgets.QSpinBox, 'spnTime')
        self.groupBox = self.findChild(QtWidgets.QGroupBox, 'groupBox')
        self.statusBar = self.findChild(QtWidgets.QStatusBar, 'statusbar')
        self.radShutdown = self.findChild(QtWidgets.QRadioButton, 'radShutdown')
        self.radRestart = self.findChild(QtWidgets.QRadioButton, 'radRestart')
        self.radSleep = self.findChild(QtWidgets.QRadioButton, 'radSleep')
        self.radHibernate = self.findChild(QtWidgets.QRadioButton, 'radHibernate')
        self.sldBrightness = self.findChild(QtWidgets.QSlider, 'sldBrightness')
        self.lblBrightness = self.findChild(QtWidgets.QLabel, 'lblBrightness')
        self.btnBrightness = self.findChild(QtWidgets.QPushButton, 'btnBrightness')
        self.grpBrightness = self.findChild(QtWidgets.QGroupBox, 'grpBrightness')
        self.btnEnable = self.findChild(QtWidgets.QPushButton, 'btnEnable')
        self.chkVolume = self.findChild(QtWidgets.QCheckBox, 'chkVolume')
        self.btnStart.clicked.connect(self.btnPressed)
        self.btnBrightness.clicked.connect(self.btnBrightnessPressed)
        self.sldBrightness.valueChanged.connect(self.brightnessChanged)
        self.btnUp.clicked.connect(self.btnChangeMinsUp)
        self.btnDown.clicked.connect(self.btnChangeMinsDown)
        self.btnEnable.clicked.connect(self.enableBrightness)
        self.spnTime.valueChanged.connect(self.timeChanged)
        self.grpBrightness.setEnabled(False)
        self.lblBrightness.setEnabled(False)
        self.sldBrightness.setEnabled(False)
        self.btnBrightness.setEnabled(False)
        self.active = False

        #Figure out how many steps to reduce volume, it's very hacky!
        if os.name == 'nt':
            self.audioSteps = [59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11]
        else:
            #assumes 20 steps
            self.audioSteps = [58, 55, 52, 49, 46, 43, 40, 37, 34, 31, 28, 25, 22, 19, 16, 13, 10, 7, 4, 1]

        self.show()
        
    #Update the minute text if the dial is moved    
    def sliderMoved(self):
        self.spnTime.setValue(int(self.dial.value()))
    
    #Use buttons on each side for fine control
    def btnChangeMinsUp(self):
        self.spnTime.setValue(self.spnTime.value() + 1)
    
    def btnChangeMinsDown(self):
        self.spnTime.setValue(self.spnTime.value() - 1)

    def btnBrightnessPressed(self):
        sbc.set_brightness(int(self.lblBrightness.text()))

    def brightnessChanged(self):
        self.lblBrightness.setText(str(self.sldBrightness.value()))

    def enableBrightness(self):
        if self.btnEnable.isChecked():
            print('hello')
            self.grpBrightness.setEnabled(True)
            self.btnBrightness.setEnabled(True)
            self.lblBrightness.setEnabled(True)
            self.sldBrightness.setEnabled(True)
        else:
            self.grpBrightness.setEnabled(False)
            self.lblBrightness.setEnabled(False)
            self.sldBrightness.setEnabled(False)
            self.btnBrightness.setEnabled(False)

    # Button press routine
    def btnPressed(self):
        global timeSet 

        if self.active == False:
            timeSet = int(self.spnTime.value())
            self.btnStart.setText("Cancel")
            self.spnTime.setEnabled(False)
            self.dialMins.setEnabled(False)
            self.groupBox.setEnabled(False)
            self.active = True
            self.timer0 = QtCore.QTimer()
            self.time = QtCore.QTime(0, 0, 0)
            self.time = self.time.addSecs(int(self.spnTime.value()) * 60)
            self.timer0.setInterval(1000)
            self.timer0.timeout.connect(lambda:self.ticker())
            self.timer0.start()
        else:
            self.btnStart.setText("Set Timer")
            self.active = False
            self.spnTime.setEnabled(True)
            self.dialMins.setEnabled(True)
            self.groupBox.setEnabled(True)
            self.statusBar.clearMessage()
            self.spnTime.setValue(timeSet)

    #Make dial follow the minute text
    def timeChanged(self):
        self.dial.setValue(self.spnTime.value())

    #define shutdown types
    def osShutdown(self):
        print("Shutdown!")
        if os.name == 'nt':
            os.system("shutdown /s /t 10")
        else: 
            os.system("systemctl poweroff")
    def osRestart(self):
        print("Restarting!")
        if os.name == 'nt':
            os.system("shutdown /r /t 10")
        else:
            os.system("systemctl reboot")
    def osSleep(self):
        print("Sleeping!")
        if os.name == 'nt':
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            os.system("systemctl suspend")
    def osHibernate(self):
        print("Hibernating!")
        if os.name == 'nt':
            os.system("rundll32.exe powrprof.dll,SetSuspendState 1,1,0")
        else:
            os.system("systemctl hibernate")
    def osReduceVolume(self):
        if self.chkVolume.isChecked():
            if os.name == 'nt':
                keyboard.press_and_release('volume down')
            else:
                os.system("xdotool key XF86AudioLowerVolume")
            del self.audioSteps[0]
    def osPausePlayback(self):
        if os.name == 'nt':
            keyboard.press_and_release('play/pause media')
        else:
            os.system("xdotool key XF86AudioPlay")
    
    # on each tick, what to do
    def ticker(self):
        if self.active == True:
            global time
            self.spnTime.setValue((int(self.time.toString("hh")) * 60) + int(self.time.toString("mm")))
            if self.time.second() == 0 and self.time.minute() == 0 and self.time.hour() == 0:
                self.osPausePlayback()
                if self.radShutdown.isChecked():
                    self.osShutdown()
                if self.radRestart.isChecked():
                    self.osRestart()
                if self.radSleep.isChecked():
                    self.osSleep()
                if self.radHibernate.isChecked():
                    self.osHibernate()
                exit()
            if len(self.audioSteps) > 0:
                if self.time.second() == self.audioSteps[0] and self.time.minute() < 1 and self.time.hour() == 0:
                    self.osReduceVolume()
            self.time = self.time.addSecs(-1)
            self.statusBar.showMessage("Time Remaining: " + self.time.toString("hh:mm:ss",))


active = False
app = QtWidgets.QApplication(sys.argv)
app.setStyle('Breeze')
window = Ui()
app.exec_()

