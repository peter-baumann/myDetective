"""
Requires PyQt4 library. Download from http://www.riverbankcomputing.com/software/pyqt/download

Last edit: 7 Nov 2012
"""

import sys, random, os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from svmtools.svmutil import *
import pca as pcaplot


# Worker threads
class TestDocWorker(QThread):
    done = pyqtSignal(object)
    msg = pyqtSignal(str)
    
    def __init__(self, doc, model, meanVect, stdVect):
        self.doc = doc
        self.model = model
        self.meanVect = meanVect
        self.stdVect = stdVect
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        from Main import *
        self.msg.emit("Running svm test..")
        setMode(Mode.FunctionWordFrequency)

        self.msg.emit("Converting to attribute vector..")
        value = getAttributeVector(self.doc)
        value = [float(i) for i in value]
        
        self.msg.emit("Normalising values..")
        # Normalize data
        value = normalise("apply", [value], self.meanVect, self.stdVect)

        self.msg.emit("Predicting..")
        pred = svmtest(value, self.model)

        self.msg.emit("Prediction complete.")
        self.done.emit(pred)


class TrainModelWorker(QThread):
    done = pyqtSignal(object, object, object, object, object, object)
    msg = pyqtSignal(str)

    def __init__(self, trainFolder, testFolder):
        self.trainFolder = trainFolder + "/"
        self.testFolder = testFolder + "/"
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        from Main import *
        setMode(Mode.FunctionWordFrequency)

        self.msg.emit("Extracting vectors...")        
        trlabels, trvalues, trAuthorList = extractVectors(self.trainFolder)
        tslabels, tsvalues, tsAuthorList = extractVectors(self.testFolder)

        labels = []
        values = []
        labels.extend(trlabels)
        labels.extend(tslabels)
        values.extend(trvalues)
        values.extend(tsvalues)
        
        try:
            self.msg.emit("Collating data..")

            authors = [dict() for i in range(len(trAuthorList))]

            for i in range(len(values)):
                authors[int(labels[i]) - 1]["Essay " + str(i)] = values[i]

            data = dict()
            for i in range(len(trAuthorList)):
                data[trAuthorList[i]] = authors[i]
        except Exception as e:
            self.msg.emit("Exception: " + str(e))
            return
        
        self.msg.emit("Normalising values..")
        # Normalize data
        values, meanVect, stdVect = normalise(values)
        
        self.msg.emit("Training model..")        
        model, acc = xTrain(labels, values, 5, True)

        self.msg.emit("Training completed.")
        self.done.emit(model, acc, trAuthorList, data, meanVect, stdVect)

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
        font: 75 18pt;\
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

class TrainWindow(QMainWindow):
    def __init__(self, indices):
        QWidget.__init__(self)
        self.indices = indices
        self.initUI()

    def initUI(self):
        self.pics = [QPixmap("images/author_" + str(int(i + 1)) + ".jpg").scaled(300, 188, Qt.KeepAspectRatio) for i in range(self.indices)]
        self.mc = QWidget(self)
        self.labelTxt = QLabel("System working in progress", self.mc)
        self.labelTxt.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelTxt.setStyleSheet("font-size: 18px;")
        self.labelPic = QLabel(self.mc)
        self.labelPic.setPixmap(self.pics[0])
        self.labelTxt.resize(212,92)

        mainLayer = QVBoxLayout()
        mainLayer.addWidget(self.labelTxt, 2, Qt.AlignHCenter)
        mainLayer.addWidget(self.labelPic, 8, Qt.AlignHCenter)
        self.mc.setLayout(mainLayer)
        
        self.timer = QBasicTimer()
        self.timer.start(100, self)

        # Frame settings
        self.setCentralWidget(self.mc)
        self.setStyleSheet("QMainWindow{ border: 1px solid black;}")

        # Window flag settings
        flags = Qt.WindowFlags()
        flags |= Qt.FramelessWindowHint # Make frameless
        self.setWindowFlags(flags)  # Set the flag

        self.setGeometry(408, 280, 300, 300)
        self.center()

    def closeEvent(self, e):
        if self.timer.isActive():
            self.timer.stop()

    def timerEvent(self, e):
        index = random.randint(0, self.indices - 1)
        self.labelPic.setPixmap(self.pics[index])
        self.update()

    def center(self):
        # Centralize main window frame
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
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

class TestWindow(QMainWindow):
    def __init__(self, index, authorName):
        QWidget.__init__(self)
        self.index = index
        self.authorName = authorName
        self.initUI()

    def initUI(self):
        self.mc = QWidget(self)
        self.pic = QPixmap("images/author_" + str(int(self.index)) + ".jpg")
        self.pic = self.pic.scaled(300, 188, Qt.KeepAspectRatio)
        self.labelTxt = QLabel("The system \nevaluted that the \nfollowing person is \nthe most similar", self.mc)
        self.labelTxt.setStyleSheet("font-size: 14px;")
        self.labelPic = QLabel(self.mc)
        self.labelPic.setPixmap(self.pic)
        self.labelTxt.resize(212,92)
        self.labelAuthor = QLabel(self.authorName, self.mc)
        self.labelAuthor.setStyleSheet("background-color: black; color: white; border: 3px solid white; border-radius: 8px; font-size: 18px;")
        self.labelAuthor.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelAuthor.setMaximumSize(212, 84)
        self.labelAuthor.setMinimumSize(212, 84)
        
        buttonLayer = QHBoxLayout()
        closeBut = RoundButton("x", self.mc)
        self.emptySpace = QLabel()
        buttonLayer.addWidget(self.emptySpace, 9)
        buttonLayer.addWidget(closeBut, 1)

        vbox = QVBoxLayout()
        vbox.addWidget(self.labelTxt, 1, Qt.AlignHCenter)
        vbox.addWidget(self.labelAuthor, 1, Qt.AlignTop)
        
        hbox = QHBoxLayout()
        hbox.addLayout(vbox, 4)        
        hbox.addWidget(self.labelPic, 5)

        mainLayer = QVBoxLayout()
        mainLayer.addLayout(buttonLayer, 1)
        mainLayer.addLayout(hbox, 9)
        self.mc.setLayout(mainLayer)

        closeBut.clicked.connect(self.close)        


        # Frame settings
        self.setCentralWidget(self.mc)
        self.setStyleSheet("QMainWindow{ border: 1px solid black;}")

        # Window flag settings
        flags = Qt.WindowFlags()
        flags |= Qt.FramelessWindowHint # Make frameless
        self.setWindowFlags(flags)  # Set the flag

        self.setGeometry(560, 280, 300, 300)
        self.center()

    def center(self):
        # Centralize main window frame
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or (not self.childAt(event.pos()) and self.childAt(event.pos()) != self.emptySpace):
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

        # Directories variables
        self.trainDir = None
        self.testDir = None
        self.testDoc = None

        # Other variables
        self.model = None
        self.author_list = None
        self.data = None
        self.meanVect = None
        self.stdVect = None

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
        
        # Components settings
        self.trainBut.setEnabled(False)
        self.catBut.setEnabled(False)
        self.visBut.setEnabled(True)
        self.testBut.setEnabled(False)

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
        self.trainFolderBut.clicked.connect(self.trainDirDialog)
        self.testFolderBut.clicked.connect(self.testDirDialog)
        self.trainBut.clicked.connect(self.startTraining)
        self.catBut.clicked.connect(self.setTestDoc)
        self.testBut.clicked.connect(self.doTest)
        self.visBut.clicked.connect(self.plotPCA)

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

    def plotPCA(self):
        pca = pcaplot.PCAPlot(self.testDoc)
        pca.plot()

    def startTraining(self):
        self.trainBut.setEnabled(False)
        self.trainFolderBut.setEnabled(False)
        self.testFolderBut.setEnabled(False)
        worker = TrainModelWorker(self.trainDir, self.testDir)
        worker.done.connect(self.trainComplete)
        worker.msg.connect(self.showMessage)
        worker.start()
        self.trainWin = TrainWindow(10)
        self.trainWin.show()

    def showMessage(self, text):
        print text

    def trainComplete(self, model, acc, author_list, data, meanVect, stdVect):
        self.model = model
        self.author_list = author_list
        self.data = data
        self.meanVect = meanVect
        self.stdVect = stdVect

# No longer needed with new PCA solution
#        if len(data) > len(data[data.keys()[0]]):
#            self.visBut.setEnabled(True)
#        else:
#            self.visBut.setEnabled(False)

        self.accInd.setText(format(acc, ".2f") + "%")
        self.accInd.setGreen(True)
        self.trainBut.setEnabled(True)
        self.catBut.setEnabled(True)
        self.trainFolderBut.setEnabled(True)
        self.testFolderBut.setEnabled(True)
        self.trainWin.close()

    def setTestDoc(self):
        fDialog = QFileDialog()
        doc = fDialog.getOpenFileName(self, "Select the document to categorise", self.testDir)

        if doc:
            self.testDoc = doc
            self.catInd.setGreen(True)
            self.testBut.setEnabled(True)

            from Main import *
            # Add data file as unknown data
            value = getAttributeVector(self.testDoc)            
            self.data["unknown"] = dict("essay 1", value)


    def doTest(self):
        if self.testDoc:
            self.catBut.setEnabled(False)
            self.trainBut.setEnabled(False)
            self.testBut.setEnabled(False)
            self.trainFolderBut.setEnabled(False)
            self.testFolderBut.setEnabled(False)
            worker = TestDocWorker(self.testDoc, self.model, self.meanVect, self.stdVect)
            worker.done.connect(self.testComplete)
            worker.msg.connect(self.showMessage)
            worker.start()

    def testComplete(self, label):
        self.testWin = TestWindow(label[0], self.author_list[int(label[0]) - 1])
        self.testWin.show()
        self.catBut.setEnabled(True)
        self.trainBut.setEnabled(True)
        self.trainFolderBut.setEnabled(True)
        self.testFolderBut.setEnabled(True)
        self.testBut.setEnabled(True)

    def checkTrainAndTestAvail(self):
        if self.trainDir != None and self.testDir != None:
            self.trainBut.setEnabled(True)
        else:
            self.trainBut.setEnabled(False)

    def center(self):
        # Centralize main window frame
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def trainDirDialog(self):
        fDialog = QFileDialog()
        fDialog.setOption(QFileDialog.ShowDirsOnly, True)
        dir = fDialog.getExistingDirectory(self, "Select the training directory")

        if dir:
            self.trainDir = str(dir)
            self.trainFolderInd.setGreen(True)

        self.checkTrainAndTestAvail()

    def testDirDialog(self):
        fDialog = QFileDialog()
        fDialog.setOption(QFileDialog.ShowDirsOnly, True)
        dir = fDialog.getExistingDirectory(self, "Select the testing directory")

        if dir:
            self.testDir = str(dir)
            self.testFolderInd.setGreen(True)

        self.checkTrainAndTestAvail()

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
    splashScreen = QSplashScreen(QPixmap("images/splash.png"))
    splashScreen.show()
    app.processEvents()

    # Long imports here
    from Main import *
    print " done"

    frame = MainFrame()
    splashScreen.finish(frame)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
