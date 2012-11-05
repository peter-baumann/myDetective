"""
Requires PyQt4 library. Download from http://www.riverbankcomputing.com/software/pyqt/download

Last edit: 3 Nov 2012
"""

import sys, random
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class RoundButton(QPushButton):
    normColor = "#4f81bd"
    overColor = "#8eb4e3"
    downColor = "#88a0bd"
    
    def __init__(self, parent=None):
        super(RoundButton, self).__init__(parent)
        self.initUI()

    def __init__(self, text, parent=None):
        super(RoundButton, self).__init__(text, parent)
        self.initUI()

    def initUI(self):
        self.setMaximumSize(28, 28)
        self.setMinimumSize(28, 28)

        css =   "RoundButton{ padding: 4px;\
        background-color: " + RoundButton.normColor + ";\
        border-radius: 14px;\
        border: 3px solid white;\
        color: white;\
        font: 98 11pt;\
        }\
        RoundButton:hover{\
        background-color: " + RoundButton.overColor + ";\
        }\
        RoundButton:pressed{\
        background-color: " + RoundButton.downColor + ";\
        }"

        self.setStyleSheet(css)

class Indicator(QLabel):
    green = "#9bbb59"
    red = "#c0504d"

    def __init__(self, defWidth=38, defHeight=38, defState=False, parent=None):
        super(Indicator, self).__init__(parent)
        self.w = defWidth
        self.h = defHeight
        self.state = defState
        self.initUI()

    def initUI(self):
        css = self.getCss(self.state)
        self.setStyleSheet(css)
        self.setMaximumSize(self.w, self.h)
        self.setMinimumSize(self.w, self.h)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def getCss(self, state):
        css = "Indicator {\
        background-color: ";

        if state:
            css += Indicator.green + ";"
        else:
            css += Indicator.red + ";"

        css += "border: 4px solid white;\
        border-radius: 6px;\
        color: white;\
        }"

        return css

    def setGreen(self, state):
        css = self.getCss(state)
        self.setStyleSheet(css)
        self.update()

class AccCircle(Indicator):

    def __init__(self, defRadius=83, defState=False, parent=None):
        #self.state = defState
        self.radius = defRadius
        super(AccCircle, self).__init__(defState, parent)
        #self.initUI()

    def initUI(self):
        css = self.getCss(self.state)
        self.setStyleSheet(css)
        self.setMaximumSize(self.radius, self.radius)
        self.setMinimumSize(self.radius, self.radius)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def getCss(self, state):
        bRad = self.radius / 2;

        if (self.radius % 2) == 1:
            bRad -= 1

        css = "AccCircle {\
        background-color: ";

        if state:
            css += Indicator.green + ";"
        else:
            css += Indicator.red + ";"

        css += "border: 4px solid white;\
        border-radius: " + str(bRad) + "px;\
        color: white;\
        font: 75 23pt;\
        }"

        return css

class Button(QPushButton):
    def __init__(self, text=None, defW=150, defH=30, defFont=None, parent=None):
        """
        if text:
            c = 8
            if defFont:
                c = defFont.pixelSize()
            if len(text) * 1 / 2.0 * c > (defW - 4):
                maxLen = int((defW - 4.0) / (1.0/2 * c))
                curPointer = 0
                text_out = ""
                while curPointer + maxLen < len(text):
                    text_out += text[curPointer:curPointer + maxLen] + "\n"
                    curPointer += maxLen
                text_out += text[curPointer:len(text)]
                text = text_out
        """
                
        super(Button, self).__init__(text, parent)
        self.w = defW;
        self.h = defH;
        self.initUI(defFont)

    def initUI(self, font):
        self.setMaximumSize(self.w, self.h)
        self.setMinimumSize(self.w, self.h)

        if font:
            fontSize = font.pixelSize()
            fontWeight = font.weight()
            fontFamily = font.family()

        css =   "Button{ padding: 4px; background-color: #e6e6e6;\
        border-radius: 5px;\
        border: 1px solid black;\
        font: " + str(fontWeight) + " " + str(fontSize) + "px \"" + str(fontFamily) + "\";\
        }\
        Button:hover{\
        background-color: #d9d9d9;\
        }\
        Button:pressed{\
        background-color: #b7b7b7;\
        }"

        self.setStyleSheet(css)

class MainFrame(QMainWindow):
    def __init__(self):
        super(MainFrame, self).__init__()
        self.initUI()

    def initUI(self):
        # Setup GUI
        
        self.allowMove = False;
        self.offset = QPoint()

        # Container 
        self.mainContainer = QWidget(self)
        mc = self.mainContainer

        grid = QGridLayout()
        hbox = QHBoxLayout()

        # Components
        minimize = RoundButton("-", mc)
        close = RoundButton("x", mc)

        font = QFont()
        font.setFamily("helvetica")
        font.setWeight(QFont.DemiBold)
        font.setPixelSize(18)

        self.trainFolderBut = Button("Insert Training data", 252, 48, font, mc)
        self.testFolderBut = Button("Insert Testing data", 252, 48, font, mc)
        self.trainBut = Button("Train && Test System", 252, 48, font, mc)
        
        font.setPixelSize(16)
        self.catBut = Button("Insert file for categorization", 252, 48, font, mc)

        self.trainFolderInd = Indicator(48, 48, False, mc)
        self.testFolderInd = Indicator(48, 48, False, mc)
        self.catInd = Indicator(48, 48, False, mc)

        self.accLbl = QLabel("Accuracy of the System", mc)
        self.accLbl.setStyleSheet("font-size: 14px")

        self.accInd = AccCircle(92, False, mc)
        self.accInd.setText("-")
        
        font.setPixelSize(14)
        self.visBut = Button("Overall Doc \nVisualization", 136, 48, font, mc)
        self.testBut = Button("Test file", 136, 48, font, mc)
        
        self.emptySpace = QLabel()
        # Layout
        hbox.addWidget(self.emptySpace, 1)
        hbox.addWidget(minimize, 1)
        hbox.addWidget(close, 1)
        grid.addLayout(hbox, 0, 4)

        grid.addWidget(self.trainFolderBut, 1, 0)
        grid.addWidget(self.testFolderBut, 2, 0)
        grid.addWidget(self.trainBut, 3, 0)
        grid.addWidget(self.catBut, 4, 0)

        grid.addWidget(self.trainFolderInd, 1, 3)
        grid.addWidget(self.testFolderInd, 2, 3)
        grid.addWidget(self.catInd, 4, 3)

        grid.addWidget(self.accLbl, 1, 4, Qt.AlignHCenter)
        grid.addWidget(self.accInd, 2, 4, Qt.AlignHCenter)
        grid.addWidget(self.visBut, 3, 4, Qt.AlignHCenter)
        grid.addWidget(self.testBut, 4, 4, Qt.AlignHCenter)
                        
        mc.setLayout(grid)

        # Event registration
        close.clicked.connect(QCoreApplication.instance().quit)        
        minimize.clicked.connect(self.showMinimized)


        # Container is central object
        self.setCentralWidget(self.mainContainer)
        
        # Frame settings

        self.setStyleSheet("QMainWindow{border: 1px solid black;}")

        # Window flag settings
        flags = Qt.WindowFlags()
        flags |= Qt.FramelessWindowHint # Make frameless
        self.setWindowFlags(flags)  # Set the flag

        self.setGeometry(300, 300, 612, 280)
        self.center()
        self.setWindowTitle("My Detective")
        self.show()

    def center(self):
        # Centralize main window frame
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or self.childAt(event.pos()) != self.mainContainer and self.childAt(event.pos()) != self.emptySpace:
            return

        self.allowMove = True
        self.offset = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        self.allowMove = False

    def mouseMoveEvent(self, event):
        if not self.allowMove:
            return

        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x-x_w, y-y_w)

def main():
    app = QApplication(sys.argv)
    frame = MainFrame()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()