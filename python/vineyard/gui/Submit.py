#!/usr/bin/python

import sys, os
from PyQt4 import QtGui, QtCore
from vineyard.engines.BaseEngines import EngineRegistry

class SubmitWidget(QtGui.QWidget):
    
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        
        self.main_layout = QtGui.QVBoxLayout()
        
        engGroup = QtGui.QGroupBox("Available Engines")
        self.engine_cb = QtGui.QComboBox()
        self.stack = QtGui.QStackedWidget(self)
        
        #for eng in getEngineList():
        for eng in EngineRegistry.getRegistry():
            self.engine_cb.addItem(eng.name)
            self.engine_cb.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
            widget = self.buildSubmitForm(eng)
            self.stack.addWidget(widget)
                                 
        hbox = QtGui.QHBoxLayout()
        englabel = QtGui.QLabel("Engines:")
        englabel.setAlignment(QtCore.Qt.AlignRight)
        hbox.addWidget(englabel)
        hbox.addWidget(self.engine_cb)
        engGroup.setLayout(hbox)
        #self.engine_cb.setCurrentIndex(-1)        
        self.main_layout.addWidget(engGroup)            
        self.main_layout.addWidget(self.stack)        
        sjb = QtGui.QPushButton("Submit Job")  
        sjb.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sjb.setStatusTip(self.tr("Submit a job to the farm"))
        self.main_layout.addWidget(sjb)
        self.main_layout.addStretch()
        self.main_layout.setMargin(2)
        self.setLayout(self.main_layout)
        
        self.connect(sjb, QtCore.SIGNAL("clicked()"), self.submitJob)
        
        bsf = lambda e: self.buildSubmitForm(EngineRegistry.getEngineByName(self.engine_cb.currentText()))
        self.connect(self.engine_cb, QtCore.SIGNAL("currentIndexChanged(int)"), self.stack.setCurrentIndex)

        
    def buildSubmitForm(self, eng):
        #print 'building the submit form for', eng
        #try:
            #if eng and type(eng.commandFormat) == list:
                ##print 'command format found', eng.commandFormat
                
                #submit_form = QtGui.QGroupBox("Submit Options")
                #vbox = QtGui.QVBoxLayout()    
                
                ##def addLOItem(isi0, le):
                    ##if type(isi0) == str:
                        ##isi0 = [isi0, le]
                    ##elif type(isi0) == list and len(isi0) > 1:
                        ##isi0 = [isi0[0], le]                

                #def makeCbEnabler(control):
                    #cb = QtGui.QCheckBox()
                    #self.connect(cb, QtCore.SIGNAL("stateChanged(int)"), control.setEnabled)
                    #control.setEnabled(cb.isChecked())
                    #return cb
                    
               ##def formatLO(isi0, le, hbox, bReq):                
                    ##le.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
                    ##addLOItem(isi0, le)
                    ##hbox.addWidget(le)
                    ##if not bReq: 
                        ##cb = makeCbEnabler(le, isi0)
                        ##hbox.addWidget(le)
                
                #for item in eng.commandFormat:
                    #if type(item) == dict:
                        #for subitem in item:
                            #hbox = QtGui.QHBoxLayout()
                            #label = QtGui.QLabel(str(subitem))
                            #label.setAlignment(QtCore.Qt.AlignRight)
                            #hbox.addWidget(label)
                            
                            #bReq = False
                            #if len(item[subitem]) >= 3:
                                #bReq = str(item[subitem][2]).lower() == 'required'
                                
                            #if len(item[subitem]) >= 4 and type(item[subitem][3]) == list and len(item[subitem][3]) > 1:
                                    #le = QtGui.QComboBox(submit_form)
                                    #le.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
                                    #if type(item[subitem][0]) == str:
                                        #item[subitem][0] = [item[subitem][0], le]
                                    #elif type(item[subitem][0]) == list and len(item[subitem][0]) > 1:
                                        #item[subitem][0] = [item[subitem][0][0], le]
                                    #hbox.addWidget(le)
                                    #if not bReq: 
                                        #cb = makeCbEnabler(le)
                                        #if type(item[subitem][0]) == list and len(item[subitem][0]) > 1:
                                            #item[subitem][0] = [item[subitem][0][0], item[subitem][0][1], cb]
                                        #hbox.addWidget(cb)
                            #elif len(item[subitem]) >= 2:
                                ## this item is a text field for manual entry, or a spinner, if this is a int or float
                                #if item[subitem][1] == 'str' or item[subitem][1] == 'float':
                                    ## text field
                                    #le = QtGui.QLineEdit(submit_form)
                                    #le.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
                                    #if type(item[subitem][0]) == str:
                                        #item[subitem][0] = [item[subitem][0], le]
                                    #elif type(item[subitem][0]) == list and len(item[subitem][0]) > 1:
                                        #item[subitem][0] = [item[subitem][0][0], le]
                                    #hbox.addWidget(le)
                                    #if not bReq: 
                                        #cb = makeCbEnabler(le)
                                        #if type(item[subitem][0]) == list and len(item[subitem][0]) > 1:
                                            #item[subitem][0] = [item[subitem][0][0], item[subitem][0][1], cb]
                                        #hbox.addWidget(cb)
                                #elif item[subitem][1] == 'int':
                                    ## int spinner
                                    #le = QtGui.QSpinBox(submit_form)
                                    #le.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
                                    #if type(item[subitem][0]) == str:
                                        #item[subitem][0] = [item[subitem][0], le]
                                    #elif type(item[subitem][0]) == list and len(item[subitem][0]) > 1:
                                        #item[subitem][0] = [item[subitem][0][0], le]
                                    #hbox.addWidget(le)
                                    #if not bReq: 
                                        #cb = makeCbEnabler(le)
                                        #if type(item[subitem][0]) == list and len(item[subitem][0]) > 1:
                                            #item[subitem][0] = [item[subitem][0][0], item[subitem][0][1], cb]
                                        #hbox.addWidget(cb)
                                #elif item[subitem][1] == 'bool':
                                    ## checkbox
                                    #le = QtGui.QCheckBox(submit_form)
                                    #if type(item[subitem][0]) == str:
                                        #item[subitem][0] = [item[subitem][0], le]
                                    #elif type(item[subitem][0]) == list and len(item[subitem][0]) > 1:
                                        #item[subitem][0] = [item[subitem][0][0], le]
                                    #hbox.addWidget(le)
                                    #hbox.addStretch()
                            #vbox.addLayout(hbox)
                #submit_form.setLayout(vbox)
                #submit_form.setAcceptDrops(True)
                #return submit_form
                
        #except Exception, e:
            #print e
        win = eng.buildGui()
        if win:
            return win
        else:
            return QtGui.QWidget(self)
        
    def submitJob(self):
        idx = self.stack.currentIndex()
        if idx > -1:
            #print type(self.parent())
            #self.parent.status('validating job')
            self.emit(QtCore.SIGNAL("showMessage(QString)"), 'Validating job for submission')

            eng = EngineRegistry.getEngineByName(str(self.engine_cb.currentText()))
            #print eng.commandFormat
            for item in eng.commandFormat:
                if type(item) == dict:
                    for subitem in item:
                        ioi = item[subitem][0]
                        if type(ioi) == list:
                            if len(ioi) == 2:
                                #this is a required item, validate the field
                                if item[subitem][1] == 'str':
                                    # check for a string
                                    val = str(ioi[1].text())
                                    if val.strip() == '':
                                        alert = QtGui.QMessageBox.critical(self, 'INVALID JOB!', str(ioi[0]) + ' must be set!')
                                        return False
                            elif len(ioi) == 3:
                                #this is an optional item
                                if ioi[2].isChecked():
                                    #validate this field
                                    if item[subitem][1] == 'str':
                                        # check for a string
                                        print ioi
                                        val = str(ioi[1].text())
                                        if val.strip() == '':
                                            alert = QtGui.QMessageBox.critical(self, 'INVALID JOB!', str(ioi[0]) + ' must be set!')
                                            return False
                                else: 
                                    # is this a boolean? just add it, shouldn't hurt
                                    try:
                                        val = ioi[2].isChecked()
                                    except: pass
                                    # otherwise ignore it
        
                    self.emit(QtCore.SIGNAL("showMessage(QString)"), 'Job submitted successfully')
                    return True
        alert = QtGui.QMessageBox.critical(self, 'INVALID COMMAND FORMAT!', str(eng.name) + " does not have a correct command format! Submission aborted.")
        return False
            
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv) 
    w = SubmitWidget() 
    w.setWindowTitle('Vineyard :: Submit Widget')
    if os.path.exists('grapes.png'):
        w.setWindowIcon(QtGui.QIcon('grapes.png'))
    elif os.path.exists('gui/grapes.png'):
        w.setWindowIcon(QtGui.QIcon('gui/grapes.png'))
        
    w.show() 
    sys.exit(app.exec_()) 