import sys, copy
from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
from PyQt5.QtCore import QMimeData, QPoint, Qt, QThread, pyqtSlot, pyqtSignal, QRect
from PyQt5.QtGui import QDrag, QPixmap, QColor, QTextCharFormat
from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QWidget, QSplashScreen
from collections import OrderedDict
from demorphy.analyzer import Analyzer

import rsc, splash_rsc
from data_class import Data

mainStyleSheet = ("QWidget\n"
                  "{\n"
                  "background-color: rgb(255, 255, 255);\n"
                  "selection-background-color: rgb(0, 0, 0);\n"
                  "}\n"
                  "\n"
                  "QTextEdit\n"
                  "{\n"
                  "font: 14pt \"Cambria\";\n"
                  "border-radius: 10px;\n"
                  "background-color: rgb(255, 255, 255);\n"
                  "padding-left:5px;\n"
                  "padding-right:5px;\n"
                  "padding-top:5px;\n"
                  "padding-bottom:5px;\n"
                  "margin-right: 10px;\n"
                  "}\n"
                  "\n"
                  "QTextEdit#engBox\n"
                  "{\n"
                  "margin-bottom: 10px;"
                  "}\n"
                  "\n"
                  "QTextEdit#resultBox\n"
                  "{\n"
                  "margin-bottom: 10px;"
                  "margin-right: 10px;"
                  "}\n"
                  "\n"
                  "QLineEdit\n"
                  "{\n"
                  "font: 12pt \"Cambria\";\n"
                  "padding: 5px;\n"
                  "border-bottom:2px solid rgb(0, 0, 0);\n"
                  "background-color: rgb(255, 255, 255);\n"
                  "border-radius:1px;\n"
                  "}\n"
                  "\n"
                  "QPushButton\n"
                  "{\n"
                  "border-radius:25px;\n"
                  "color: rgb(0,0,0);\n"
                  "border:0px solid black;\n"
                  "background-color: rgb(255, 255, 255);\n"
                  "font: 12 48pt \"Source Sans Pro ExtraLight\";\n"
                  "}\n"
                  "\n"
                  "QPushButton:pressed\n"
                  "{\n"
                  "border-radius:25px;\n"
                  "color: rgb(255,255,255);\n"
                  "background-color: rgb(0, 0, 0);\n"
                  "font: 12 48pt \"Source Sans Pro ExtraLight\";\n"
                  "}\n"
                  "\n"
                  "QPushButton#minusButton\n"
                  "{\n"
                  "border-radius:25px;\n"
                  "font: 12 52pt \"Source Sans Pro ExtraLight\";\n"
                  "padding-bottom:14px;\n"
                  "}\n"
                  "\n"
                  "QPushButton#plusButton\n"
                  "{\n"
                  "border-radius:25px;\n"
                  "padding-bottom:4px;\n"
                  "}\n"
                  "\n"
                  "QScrollBar::handle\n"
                  "{\n"
                  "min-height: 8px;\n"
                  "border-radius:4px;\n"
                  "background-color: rgb(0, 0, 0);\n"
                  "margin: 10px 4px 10px 4px;\n"
                  "}\n"
                  "\n"
                  "QScrollBar\n"
                  "{\n"
                  "border-top-right-radius:10px;\n"
                  "border-bottom-right-radius:10px;\n"
                  "background: rgb(255, 255, 255);\n"
                  "width:16px;\n"
                  "margin:0px;\n"
                  "}\n"
                  "\n"
                  "QScrollBar::add-line \n"
                  "{\n"
                  "background: none;\n"
                  "height: 0px;\n"
                  "subcontrol-position: bottom;\n"
                  "subcontrol-origin: margin;\n"
                  "}\n"
                  "\n"
                  "QScrollBar::add-page \n"
                  "{\n"
                  "background: none;\n"
                  "}\n"
                  "\n"
                  "QScrollBar::sub-line \n"
                  "{\n"
                  "background:none;\n"
                  "height: 0px;\n"
                  "subcontrol-position: top;\n"
                  "subcontrol-origin: margin;\n"
                  "}\n"
                  "\n"
                  "QScrollBar::sub-page \n"
                  "{\n"
                  "background: none;\n"
                  "}\n"
                  "\n"
                  "QSplitter::handle\n"
                  "{\n"
                  "background: transparent;\n"
                  "margin: 10px,10px,10px,10px;\n"
                  "}\n"
                  "\n"
                  "")

messages = [
    'No Results Found For:',
    '* Warning: This word result was changed in the website. Update it by deleting the word and adding it again. *',
    'An error occurred while getting your results! Please check your internet connection or update the data collection module.'

]

blankColor = [45, 52, 54, 255]
existColor = [116, 185, 255, 255]
notExistColor = [162, 155, 254, 255]
redColor = QColor(255, 118, 117)
greyColor = QColor(99, 110, 114)
greenColor = QColor(85, 239, 196)
blueColor = QColor(9, 132, 227)
purple1Color = QColor(181, 52, 113)
purple2Color = QColor(131, 52, 113)
softBlueColor1 = QColor(84, 109, 229)
softBlueColor2 = QColor(119, 139, 235)
logoColor = QColor(45, 52, 54)
paintAddColor = greenColor
paintDelColor = redColor
colorPalette = [greenColor, blueColor, purple1Color, purple2Color,
                softBlueColor1, softBlueColor2]
shadowValue = 7000
offsetDivide = 1000
blurDivide = 1200
fastDuration = 200
slowDuration = 300
evenSlowerDuration = 450
spacingText = '    '

class data():
    def qDbLike(self, tablename, cname, cvalue):
        query.prepare(
            """
            SELECT *
            FROM {tn}
            WHERE {cn} LIKE ?||'%' ESCAPE '%' OR '_' ;
            """. \
                format(tn=tablename, cn=cname)
        )
        query.addBindValue(cvalue)
        query.exec_()
        query.next()
        return query.value(cname)
    
    def qDbSearch(self, tablename, cname, cvalue):
        results = []
        query.prepare(
            """
            SELECT *
            FROM {tn}
            WHERE {cn} =? COLLATE NOCASE;
            """. \
                format(tn=tablename, cn=cname)
        )
        query.addBindValue(cvalue)
        query.exec_()
        query.next()
        num_clmns = query.record().count()
        for column in range(num_clmns):
            results.append(query.value(column))
        return results
    
    def qDbSearchAll(self, tablename, cname, cvalue):
        allResults = []
        query.prepare(
            """
            SELECT *
            FROM {tn}
            WHERE {cn} =? COLLATE NOCASE;
            """. \
                format(tn=tablename, cn=cname)
        )
        query.addBindValue(cvalue)
        query.exec_()
        while (query.next()):
            results = []
            num_clmns = query.record().count()
            for column in range(num_clmns):
                results.append(query.value(column))
            allResults.append(results)
        return allResults
    
    def getDictData(self, keyword):
        blocknums = []
        results = []
        search = dt.qDbSearchAll('dict', 'keyword', keyword)
        if search == []:
            return []
        for el in search:
            blocknums.append(el[1])
        blocknums = list(OrderedDict.fromkeys(blocknums))
        for el in blocknums:
            phrase = []
            gerdef = []
            engdef = []
            exampger = []
            exampeng = []
            dict = {'keyword': '', 'blocknum': '', 'wordname': '', 'carac': '', 'phrase': '', 'gerdef': '',
                    'engdef': '', 'exampger': '', 'exampeng': ''}
            dict['keyword'] = keyword
            dict['blocknum'] = el
            for line in search:
                if line[1] == el:
                    dict['wordname'] = line[2]
                    dict['carac'] = line[3]
                    phrase.append(line[4])
                    gerdef.append(line[5])
                    engdef.append(line[6])
                    exampger.append(line[7])
                    exampeng.append(line[8])
            dict['phrase'] = phrase
            dict['gerdef'] = gerdef
            dict['engdef'] = engdef
            dict['exampger'] = exampger
            dict['exampeng'] = exampeng
            results.append(dict)
        return results
    
    def insertUS_UW(self, gersent='none', word='none', manifestations='none'):
        query.prepare(
            """
            INSERT INTO us_uw
            VALUES (?, ?, ?);
            """
        )
        query.addBindValue(gersent)
        query.addBindValue(word)
        query.addBindValue(manifestations)
        query.exec_()
    
    def delUS_UW(self):
        key = textGer.displayedText.strip()
        results = self.qDbSearchAll('us_uw', 'gersent', key)
        for line in results:
            el = line[2]
            if el in textGer.paintAddStr:
                self.del2SC('us_uw', 'gersent', 'manifestations', key, el)
            elif '-' in el:
                sublist = el.split('-')
                newel = ''
                for subel in sublist:
                    if subel not in textGer.paintAddStr:
                        newel = newel + '-' + subel
                if newel == '':
                    self.del2SC('us_uw', 'gersent', 'manifestations', key, el)
                else:
                    newel = newel[1:]
                    self.update1V2SC('us_uw', 'gersent', 'manifestations', key, el, 'manifestations', newel)
    
    def del2SC(self, tablename, cname1, cname2, cvalue1, cvalue2):
        query.prepare(
            """
            DELETE
            FROM {tn}
            WHERE {c1} =? AND {c2} =? COLLATE NOCASE;
            """. \
                format(tn=tablename, c1=cname1, c2=cname2)
        )
        query.addBindValue(cvalue1)
        query.addBindValue(cvalue2)
        query.exec_()
    
    def update1V2SC(self, tablename, cname1, cname2, cvalue1, cvalue2, uname, uvalue):
        query.prepare(
            """
            UPDATE {tn}
            SET {un} =?
            WHERE {c1} =? AND {c2} =? COLLATE NOCASE;
            """. \
                format(tn=tablename, un=uname, c1=cname1, c2=cname2)
        )
        query.addBindValue(uvalue)
        query.addBindValue(cvalue1)
        query.addBindValue(cvalue2)
        query.exec_()
    
    def insertUS(self, code='none', gersent='none', engsent='none', html='none'):
        query.prepare(
            """
            INSERT INTO us
            VALUES (?, ?, ? , ?);
            """
        )
        query.addBindValue(code)
        query.addBindValue(gersent)
        query.addBindValue(engsent)
        query.addBindValue(html)
        query.exec_()
    
    def del1SC(self, tablename, cname, cvalue):
        query.prepare(
            """
            DELETE
            FROM {tn}
            WHERE {c1} =? COLLATE NOCASE;
            """. \
                format(tn=tablename, c1=cname)
        )
        query.addBindValue(cvalue)
        query.exec_()
    
    def update1V1SC(self, tablename, cname, cvalue, uname, uvalue):
        query.prepare(
            """
            UPDATE {tn}
            SET {un} =?
            WHERE {c1} =? COLLATE NOCASE;
            """. \
                format(tn=tablename, un=uname, c1=cname)
        )
        query.addBindValue(uvalue)
        query.addBindValue(cvalue)
        query.exec_()
    
    def insertUW(self, word='none', cell='none', dict=[]):
        query.prepare(
            """
            INSERT INTO uw
            VALUES (?, ?);
            """
        )
        query.addBindValue(word)
        query.addBindValue(cell)
        query.exec_()
        for word in dict:
            keyword = word['keyword']
            blocknum = word['blocknum']
            wordname = word['wordname']
            carac = word['carac']
            numLinesPerBlock = len(word['phrase'])
            for line in range(numLinesPerBlock):
                phrase = word['phrase'][line]
                gerdef = word['gerdef'][line]
                engdef = word['engdef'][line]
                exampger = word['exampger'][line]
                exampeng = word['exampeng'][line]
                query.prepare(
                    """
                    INSERT INTO dict
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """
                )
                query.addBindValue(keyword)
                query.addBindValue(blocknum)
                query.addBindValue(wordname)
                query.addBindValue(carac)
                query.addBindValue(phrase)
                query.addBindValue(gerdef)
                query.addBindValue(engdef)
                query.addBindValue(exampger)
                query.addBindValue(exampeng)
                query.exec_()


class sqlThread(QThread):
    autoCompSignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    searchGerSignal = pyqtSignal('PyQt_PyObject')
    searchEngSignal = pyqtSignal('PyQt_PyObject')
    callFormatter = pyqtSignal()
    
    def __init__(self, parent=None):
        super(sqlThread, self).__init__(parent)
    
    def run(self):
        Ui.sqlThreadFinished = False
        while (Ui.isSqlCalled):
            Ui.isSqlCalled = False
            text = textGer.displayedText
            if Ui.sqlCallCode == 'autocomp':
                result = dt.qDbLike('us', 'gersent', text)
                self.autoCompSignal.emit(text, result)
            elif Ui.sqlCallCode == 'checkSentGer':
                result = dt.qDbSearch('us', 'gerSent', text.strip())
                if result[1] != None and result[1] != 'none' and result[1] != 'Null':
                    self.searchGerSignal.emit(result)
                    if result[2] != None and result[2] != 'none' and result[2] != 'Null':
                        self.searchEngSignal.emit(result[2])
                    else:
                        self.searchEngSignal.emit(None)
                    manifestations = dt.qDbSearchAll('us_uw', 'gersent', text.strip())
                    manifKeywords = []
                    textGer.manifestations = []
                    for el in manifestations:
                        manifKeywords.append(el[1])
                    manifKeywords = list(OrderedDict.fromkeys(manifKeywords))
                    for manifKeyword in manifKeywords:
                        subManif = []
                        for line in manifestations:
                            if line[1] == manifKeyword:
                                subManif.append(line[2])
                        t = '-'.join(cell for cell in subManif)
                        textGer.manifestations.append(t)
                    self.callFormatter.emit()
                else:
                    self.searchGerSignal.emit(None)
                    self.searchEngSignal.emit(None)
            elif Ui.sqlCallCode == 'insertUS_UW':
                dt.insertUS_UW(textGer.displayedText, resultB.displayedKeyword, textGer.paintAddStr)
                textGer.paintAddStr = ''
            elif Ui.sqlCallCode == 'delUS_UW':
                dt.delUS_UW()
                textGer.paintAddStr = ''
            elif Ui.sqlCallCode == 'insertUS-ger':
                dt.insertUS(gersent=textGer.displayedText)
            elif Ui.sqlCallCode == 'delUS-line':
                dt.del1SC('us', 'gersent', textGer.displayedText)
                dt.del1SC('us_uw', 'gersent', textGer.displayedText)
                Ui.interCallTo = 'gerBox-engBox'
                Ui.interCallCode = 'reformat'
                Ui.isInterThreadCalled = True
                Ui.interThread.start()
            elif Ui.sqlCallCode == 'updateUS':
                dt.update1V1SC('us', 'gersent', textGer.displayedText, 'engsent', textEng.displayedText.strip())
            elif Ui.sqlCallCode == 'insertUS-ger-eng':
                dt.insertUS(gersent=textGer.displayedText, engsent=textEng.displayedText.strip())
            elif Ui.sqlCallCode == 'updatUS-noeng':
                dt.update1V1SC('us', 'gersent', textGer.displayedText, 'engsent', 'none')
            elif Ui.sqlCallCode == 'insertUW':
                dt.insertUW(word=resultB.displayedKeyword, dict=resultB.displayedDict)
            elif Ui.sqlCallCode == 'delUW':
                dt.del1SC('uw', 'word', resultB.displayedKeyword)
                dt.del1SC('us_uw', 'word', resultB.displayedKeyword)
                dt.del1SC('dict', 'keyword', resultB.displayedKeyword)
    
    def __del__(self):
        self.exiting = True
        self.wait()


class interThread(QThread):
    interCallEngBox = pyqtSignal('PyQt_PyObject')
    interCallGerBox = pyqtSignal('PyQt_PyObject')
    interCallresultB = pyqtSignal('PyQt_PyObject')
    interCallsearchB = pyqtSignal('PyQt_PyObject')
    
    def __init__(self, parent=None):
        super(interThread, self).__init__(parent)
    
    def run(self):
        while (Ui.isInterThreadCalled):
            Ui.isInterThreadCalled = False
            if 'engBox' in Ui.interCallTo:
                self.interCallEngBox.emit(Ui.interCallCode)
            if 'gerBox' in Ui.interCallTo:
                self.interCallGerBox.emit(Ui.interCallCode)
            if 'resultB' in Ui.interCallTo:
                self.interCallresultB.emit(Ui.interCallCode)
            if 'searchB' in Ui.interCallTo:
                self.interCallsearchB.emit(Ui.interCallCode)
    
    def __del__(self):
        self.exiting = True
        self.wait()


class dictThread(QThread):
    dictResult = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    existsOrNotSignal = pyqtSignal('PyQt_PyObject')
    
    def __init__(self, parent=None):
        super(dictThread, self).__init__(parent)
        dictThread.searchedWord = ''
    
    def run(self):
        while (Ui.isDictCalled):
            Ui.isDictCalled = False
            toSearch = Ui.dictCallCode
            dictThread.searchedWord = toSearch
            errorCode = ''
            try:
                result = DT.scraper(toSearch)
            except:
                result = ['']
                errorCode = 'scraper_call'
            if result[0] != '':
                resultB.cleared = False
                resultB.displayedKeyword = result[0]
                resultB.displayedDict = result[1]
                for word in result[1]:
                    text2 = 'blocknum' + word['blocknum']
                    wordname = word['wordname']
                    carac = word['carac']
                    listLen = len(word['phrase'])
                    self.dictResult.emit(text2, 'wordname', wordname)
                    self.dictResult.emit(text2, 'carac', carac)
                    for num in range(listLen):
                        phrase = word['phrase'][num]
                        gerdef = word['gerdef'][num]
                        engdef = word['engdef'][num]
                        exampger = word['exampger'][num]
                        exampeng = word['exampeng'][num]
                        if phrase != None and phrase != 'none' and phrase != 'Null':
                            self.dictResult.emit(text2, 'phrase', phrase)
                        if gerdef != None and gerdef != 'none' and gerdef != 'Null':
                            self.dictResult.emit(text2, 'gerdef', gerdef)
                        if engdef != None and engdef != 'none' and engdef != 'Null':
                            self.dictResult.emit(text2, 'engdef', engdef)
                        if exampger != None and exampger != 'none' and exampger != 'Null':
                            self.dictResult.emit(text2, 'exampger', exampger)
                        if exampeng != None and exampeng != 'none' and exampeng != 'Null':
                            self.dictResult.emit(text2, 'exampeng', exampeng)
                dataResult = dt.getDictData(resultB.displayedKeyword)
                if dataResult == []:
                    self.existsOrNotSignal.emit('no')
                else:
                    if dataResult == result[1]:
                        self.existsOrNotSignal.emit('yes')
                    else:
                        self.existsOrNotSignal.emit('changed')
            elif result[0] == '' and errorCode == 'scraper_call':
                self.dictResult.emit('scraper_call_error', 'none', 'none')
            else:
                self.dictResult.emit('No Results', 'none', 'none')
    
    def __del__(self):
        self.exiting = True
        self.wait()


class label(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(label, self).__init__(parent)
        self.wanderlust = 'WANDERLUST mini'
        self.f = QtGui.QFont('broadway', 37)
        self.met = QtGui.QFontMetrics(self.f)
        self.fh = self.met.height()
        self.fh2 = self.fh / 2 + 7
        self.setMinimumSize(QtCore.QSize(self.fh2, 370))
        self.setMaximumWidth(self.fh / 2)
    
    def paintEvent(self, event):
        self.updateGeometry()
        painter = QtGui.QPainter(self)
        painter.setPen(logoColor)
        w = self.width()
        painter.setFont(self.f)
        painter.translate(w, self.height())
        painter.rotate(-90)
        painter.drawText(0, 0, self.wanderlust)
        painter.end()


class textGer(QtWidgets.QTextBrowser):
    def __init__(self, parent):
        super(textGer, self).__init__(parent)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setMinimumSize(QtCore.QSize(200, 0))
        self.setTabChangesFocus(True)
        self.setUndoRedoEnabled(True)
        self.setAcceptRichText(False)
        self.setAcceptDrops(True)
        self.setCursorWidth(2)
        self.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByKeyboard |
            QtCore.Qt.LinksAccessibleByMouse |
            QtCore.Qt.TextBrowserInteraction |
            QtCore.Qt.TextEditable |
            QtCore.Qt.TextEditorInteraction |
            QtCore.Qt.TextSelectableByKeyboard |
            QtCore.Qt.TextSelectableByMouse)
        
        textGer.isSentenceExisting = False
        textGer.isThereSentence = False
        textGer.isInserted = False
        textGer.displayedText = None
        textGer.isPaintOn = False
        textGer.paintMode = ''
        textGer.manifestations = []
        textGer.paintAddStr = ''
        textGer.paintDelStr = ''
        
        self.oldTextLength = 0
        self.newTextLength = 0
        self.caracCountAug = False
        self.compLength = 0
        self.dontComp = False
        self.color = blankColor
        self.mouseIn = False
        self.hovering = False
        self.dragMode = ''
        
        self.animation = QtCore.QVariantAnimation()
        self.animation.valueChanged.connect(self.updateStyle)
        self.textChanged.connect(self.on_textChange)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        
        Ui.sqlThread.autoCompSignal.connect(self.sqlAutoComplete)
        Ui.sqlThread.searchGerSignal.connect(self.onSearch)
        Ui.sqlThread.callFormatter.connect(self.textFormatter)
        Ui.interThread.interCallGerBox.connect(self.on_interCall)
    
    @pyqtSlot('PyQt_PyObject')
    def on_interCall(self, code):
        if code == 'paintErr':
            if self.hovering == False:
                self.animationBegin()
                timer = QtCore.QTimer()
                timer.singleShot(slowDuration, self.animationEnd)
            else:
                self.animationEnd()
                timer = QtCore.QTimer()
                timer.singleShot(slowDuration, self.animationBegin)
        if 'paintOn' in code:
            if 'add' in code:
                self.tempColor = paintAddColor
            if 'del' in code:
                self.tempColor = paintDelColor
            if self.hovering == False:
                self.shadow.setColor(self.tempColor)
                self.animationBegin()
            else:
                self.animationEnd()
                timer = QtCore.QTimer()
                timer.singleShot(slowDuration, lambda c=self.tempColor: self.animationBegin2(c))
            self.hovering = True
        if 'paintOff' in code:
            self.hovering = False
            R2 = self.color[0]
            G2 = self.color[1]
            B2 = self.color[2]
            R = self.tempColor.red()
            G = self.tempColor.green()
            B = self.tempColor.blue()
            self.animation.stop()
            self.animation.setStartValue(QRect(R, G, B, shadowValue))
            self.animation.setEndValue(QRect(R2, G2, B2, 0))
            self.animation.setDuration(evenSlowerDuration)
            self.animation.start()
            self.setText(textGer.displayedText)
            self.textFormatter()
        if 'drag' in code and textGer.isInserted == True:
            if 'add' in code:
                if textGer.isSentenceExisting == False:
                    if self.hovering == True:
                        pass
                    else:
                        self.animationBegin()
                        self.hovering = True
                else:
                    if self.hovering == False:
                        pass
                    else:
                        self.animationEnd()
                        self.hovering = False
            elif 'del' in code:
                if textGer.isSentenceExisting == True:
                    if self.hovering == True:
                        pass
                    else:
                        self.animationBegin()
                        self.hovering = True
                else:
                    if self.hovering == False:
                        pass
                    else:
                        self.animationEnd()
                        self.hovering = False
        if 'reformat' in code:
            textGer.manifestations = []
            self.setText(textGer.displayedText)
            self.textFormatter()
        if 'updateInsertion' in code:
            textGer.isSentenceExisting = True
            R2 = existColor[0]
            G2 = existColor[1]
            B2 = existColor[2]
            R = self.color[0]
            G = self.color[1]
            B = self.color[2]
            self.animation.stop()
            self.animation.setStartValue(QRect(R, G, B, shadowValue))
            self.animation.setEndValue(QRect(R2, G2, B2, shadowValue))
            self.animation.setDuration(slowDuration)
            self.animation.start()
            self.color = [R2, G2, B2, 255]
    
    @pyqtSlot()
    def on_textChange(self):
        textGer.displayedText = self.toPlainText()
        self.newTextLength = len(textGer.displayedText) - self.compLength
        if self.newTextLength > self.oldTextLength:
            self.caracCountAug = True
            self.oldTextLength = self.newTextLength
        else:
            self.caracCountAug = False
            self.oldTextLength = self.newTextLength
        if textGer.displayedText.strip() != '':
            textGer.isThereSentence = True
            if Ui.sqlThreadFinished == False:
                self.dontComp = True
            if True:
                self.dontComp = False
                Ui.isSqlCalled = True
                Ui.sqlCallCode = 'autocomp'
                Ui.sqlThread.start()
        else:
            textGer.isThereSentence = False
    
    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject')
    def sqlAutoComplete(self, text, result):
        self.compLength = 0
        if result != None:
            cl = len(result)
            rl = cl - len(text)
            self.compLength = rl
            tc = self.textCursor()
            tcp = tc.position()
            if rl != 0 and self.caracCountAug == True and self.dontComp == False:
                tc.insertText(result[-rl:])
                tc.setPosition(tcp)
                tc.setPosition(tcp + rl, QtGui.QTextCursor.KeepAnchor)
                self.setTextCursor(tc)
            else:
                self.compLength = 0
        Ui.sqlThreadFinished = True
    
    @pyqtSlot('PyQt_PyObject')
    def onSearch(self, result):
        if result != None:
            textGer.isSentenceExisting = True
            self.setText(result[1])
            R2 = existColor[0]
            G2 = existColor[1]
            B2 = existColor[2]
        else:
            self.setText(textGer.displayedText.strip())
            textGer.isSentenceExisting = False
            R2 = notExistColor[0]
            G2 = notExistColor[1]
            B2 = notExistColor[2]
        R = self.color[0]
        G = self.color[1]
        B = self.color[2]
        self.animation.stop()
        self.animation.setStartValue(QRect(R, G, B, 0))
        self.animation.setEndValue(QRect(R2, G2, B2, shadowValue))
        self.animation.setDuration(slowDuration)
        self.animation.start()
        self.hovering = True
        self.color = [R2, G2, B2, 255]
    
    @pyqtSlot()
    def textFormatter(self):
        tc = self.textCursor()
        tc.setPosition(0)
        tc.setPosition(len(textGer.displayedText), QtGui.QTextCursor.KeepAnchor)
        
        init = QTextCharFormat()
        init.setFontWeight(QtGui.QFont.Normal)
        init.setForeground(Qt.black)
        
        tc.setCharFormat(init)
        self.setFontUnderline(False)
        tc.clearSelection()
        
        paletteLength = len(colorPalette)
        x = 0
        for el in textGer.manifestations:
            list = el.split('-')
            variableFormat = QTextCharFormat()
            variableFormat.setFontWeight(QtGui.QFont.Bold)
            variableFormat.setForeground(colorPalette[x])
            for sublist in list:
                subsublist = sublist.split(',')
                tc.setPosition(int(subsublist[0]))
                tc.setPosition(int(subsublist[1]), QtGui.QTextCursor.KeepAnchor)
                tc.setCharFormat(variableFormat)
                self.setFontUnderline(False)
            x += 1
            if x == paletteLength:
                x = 0
    
    @pyqtSlot()
    def animationEnd(self):
        self.animation.stop()
        self.animation.setStartValue(QPoint(shadowValue, 0))
        self.animation.setEndValue(QPoint(0, 0))
        self.animation.setDuration(slowDuration)
        self.animation.start()
    
    @pyqtSlot()
    def animationBegin(self):
        self.animation.stop()
        self.animation.setStartValue(QPoint(0, 0))
        self.animation.setEndValue(QPoint(shadowValue, 0))
        self.animation.setDuration(slowDuration)
        self.animation.start()
    
    @pyqtSlot(QtCore.QVariant)
    def updateStyle(self, value):
        if type(value) == QPoint:
            self.shadow.setOffset(value.x() / offsetDivide)
        if type(value) == QRect:
            c = QColor(value.x(), value.y(), value.width())
            self.shadow.setColor(c)
            self.shadow.setOffset(value.height() / offsetDivide)
    
    def animationBegin2(self, color):
        self.animation.stop()
        self.shadow.setColor(color)
        self.animation.setStartValue(QPoint(0, 0))
        self.animation.setEndValue(QPoint(shadowValue, 0))
        self.animation.setDuration(slowDuration)
        self.animation.start()
    
    def mousePressEvent(self, event):
        self.cur = self.textCursor()
        super(textGer, self).mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.textCursor().hasSelection() and not self.textCursor().isCopyOf(
                self.cur):
            if textGer.isInserted == True and textGer.isPaintOn == False:
                selection = self.textCursor().selectedText()
                if (len(selection.strip().split(' ')) > 1) == False:
                    self.lemmatizer(selection.strip())
            if textGer.isInserted == True and textGer.isPaintOn == True:
                selection = self.textCursor().selectedText()
                if ' ' not in selection and (selection.strip()[0].isalpha() == True
                                             and selection.strip()[-1].isalpha() == True):
                    endingSpaces = len(selection) - len(selection.rstrip())
                    leadingSpaces = len(selection) - len(selection.lstrip())
                    selectionEnd = self.textCursor().selectionEnd() - endingSpaces
                    selectionBegin = selectionEnd - len(selection.strip())
                    tc = self.textCursor()
                    
                    self.paintModeFormatting(selection, selectionBegin, selectionEnd)
        super(textGer, self).mouseReleaseEvent(event)
    
    def ParsedResultConverter(self, result):
        list = []
        for el in result:
            dict = {}
            if el._guesser:
                dict['GUESSER'] = el.guesser
            if el._category:
                dict['CATEGORY'] = el.category
            if el._lemma:
                dict['LEMMA'] = el.lemma
            if dict != {}:
                list.append(dict)
        return list
    
    def lemmatizer(self, selection):
        isGuesser = False
        ignore_list = ['ART', 'INDEF', 'PRP', 'REL', 'DEMO']
        priority_1_list = ['PREP', 'CONJ', 'INTJ']
        priority_2_list = ['V', 'NN', 'ADJ', 'ADV', 'ORD']
        
        analyzer = Analyzer(char_subs_allowed=True)
        set = analyzer.analyze(selection)
        s = self.ParsedResultConverter(set)
        V_list = []
        NN_list = []
        ADJ_list = []
        ADV_list = []
        ORD_list = []
        OTHERS_list = []
        
        if s != []:
            if 'GUESSER' in s[0].keys():
                if selection.istitle():
                    sel = selection[0].lower() + selection[1:]
                    set2 = analyzer.analyze(sel)
                    s2 = self.ParsedResultConverter(set2)
                    if s2 != []:
                        if 'GUESSER' in s2[0].keys():
                            isGuesser = True
                        else:
                            dicts = s2
                    else:
                        dicts = s2
                else:
                    isGuesser = True
            else:
                dicts = s
        else:
            dicts = s
        
        isBreak = False
        if isGuesser == False and dicts != []:
            priority_2_results = {'V': V_list, 'NN': NN_list, 'ORD': ORD_list, 'ADJ': ADJ_list, 'ADV': ADV_list,
                                  'OTHERS': OTHERS_list}
            for dict in dicts:
                if dict['CATEGORY'] in ignore_list:
                    Ui.isDictCalled = True
                    Ui.dictCallCode = selection
                    Ui.dictThread.start()
                    isBreak = True
                    break
                elif dict['CATEGORY'] in priority_1_list:
                    Ui.isDictCalled = True
                    Ui.dictCallCode = dict['LEMMA']
                    Ui.dictThread.start()
                    isBreak = True
                    break
                else:
                    if dict['CATEGORY'] == 'V':
                        priority_2_results['V'].append(dict['LEMMA'])
                    elif dict['CATEGORY'] == 'NN':
                        priority_2_results['NN'].append(dict['LEMMA'])
                    elif dict['CATEGORY'] == 'ADJ':
                        priority_2_results['ADJ'].append(dict['LEMMA'])
                    elif dict['CATEGORY'] == 'ADV':
                        priority_2_results['ADV'].append(dict['LEMMA'])
                    elif dict['CATEGORY'] == 'ORD':
                        priority_2_results['ORD'].append(dict['LEMMA'])
                    else:
                        priority_2_results['OTHERS'].append(dict['LEMMA'])
            if not isBreak:
                for key, value in priority_2_results.items():
                    if value != []:
                        Ui.isDictCalled = True
                        Ui.dictCallCode = value[0]
                        Ui.dictThread.start()
                        break
        else:
            Ui.isDictCalled = True
            Ui.dictCallCode = selection
            Ui.dictThread.start()
    
    def paintModeFormatting(self, s, sB, sE):
        tc = self.textCursor()
        isPaintAddPass = False
        isPaintDelPass = False
        i = 0
        j = 0
        for pos in range(sB, sE):
            tc.setPosition(pos)
            if tc.charFormat().fontUnderline():
                break
            if tc.charFormat().fontWeight() == 50:
                i += 1
            if tc.charFormat().fontWeight() == 75:
                j += 1
        
        tc.setPosition(sB)
        t1 = tc.charFormat().fontWeight()
        tc.setPosition(sE)
        t2 = tc.charFormat().fontWeight()
        
        if i == len(s) or i == len(s) - 1:
            isPaintAddPass = True
        if j == len(s) or j == len(s) - 1:
            isPaintDelPass = True
        
        if textGer.paintMode == 'add':
            code = 75
        elif textGer.paintMode == 'del':
            code = 50
        
        if isPaintDelPass or isPaintAddPass:
            if textGer.paintAddStr == '':
                t = str(sB) + ',' + str(sE) + ',' + s
                self.selectionFormatter(code)
                self.moveCursor(QtGui.QTextCursor.End)
                textGer.paintAddStr = t
            else:
                t = '-' + str(sB) + ',' + str(sE) + ',' + s
                self.selectionFormatter(code)
                self.moveCursor(QtGui.QTextCursor.End)
                textGer.paintAddStr = textGer.paintAddStr + t
    
    def selectionFormatter(self, code):
        if code == 75:
            self.setFontUnderline(True)
        elif code == 50:
            variableFormat = QTextCharFormat()
            variableFormat.setFontWeight(QtGui.QFont.Normal)
            variableFormat.setForeground(Qt.black)
            self.setCurrentCharFormat(variableFormat)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and textGer.isPaintOn == True:
            Ui.interCallTo = 'searchB-engBox-gerBox'
            Ui.interCallCode = 'paintOff'
            Ui.isInterThreadCalled = True
            Ui.interThread.start()
            textGer.isPaintOn = False
            textGer.paintMode = ''
            textGer.paintAddStr = ''
            addP.buttonState = 0
            removeP.buttonState = 0
        if event.key() == QtCore.Qt.Key_Insert and textGer.isInserted == False:
            textGer.atInsertion = True
            textGer.isInserted = True
            self.setCursorWidth(0)
            
            Ui.isSqlCalled = True
            Ui.sqlCallCode = 'checkSentGer'
            Ui.sqlThread.start()
        
        if event.key() == QtCore.Qt.Key_Delete and textGer.isPaintOn == False and textGer.isInserted == True:
            self.setCursorWidth(2)
            if self.hovering == False:
                self.animationBegin()
                timer = QtCore.QTimer()
                timer.singleShot(slowDuration + 50, self.animationEnd)
            else:
                self.animationEnd()
            textGer.isInserted = False
            textGer.isSentenceExisting = False
            textGer.manifestations = []
            self.clear()
            variableFormat = QTextCharFormat()
            variableFormat.setFontWeight(QtGui.QFont.Normal)
            variableFormat.setForeground(Qt.black)
            self.setCurrentCharFormat(variableFormat)
            self.setTextInteractionFlags(
                QtCore.Qt.LinksAccessibleByKeyboard |
                QtCore.Qt.LinksAccessibleByMouse |
                QtCore.Qt.TextBrowserInteraction |
                QtCore.Qt.TextEditable |
                QtCore.Qt.TextEditorInteraction |
                QtCore.Qt.TextSelectableByKeyboard |
                QtCore.Qt.TextSelectableByMouse)
            Ui.interCallTo = 'engBox'
            Ui.interCallCode = 'hide'
            Ui.isInterThreadCalled = True
            Ui.interThread.start()
            self.hovering = False
        if textGer.isInserted == True:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ControlModifier and (event.key() == QtCore.Qt.Key_C or
                                                           event.key() == QtCore.Qt.Key_A):
                super(textGer, self).keyPressEvent(event)
            return
        
        super(textGer, self).keyPressEvent(event)
    
    def enterEvent(self, event):
        self.mouseIn = True
        if textGer.isInserted == True and textGer.isPaintOn == False and self.hovering == False:
            self.hovering = True
            self.animationBegin()
    
    def leaveEvent(self, event):
        self.mouseIn = False
        if textGer.isInserted == True and textGer.isPaintOn == False and self.hovering == True:
            textGer.atInsertion = False
            self.hovering = False
            self.animationEnd()
    
    def dragEnterEvent(self, e):
        self.dragMode = ''
        if e.mimeData().data('drag') == b'add' and textGer.isSentenceExisting == False and textGer.isInserted == True:
            e.accept()
            self.dragMode = 'add'
        elif e.mimeData().data('drag') == b'del' and textGer.isSentenceExisting == True and textGer.isInserted == True:
            e.accept()
            self.dragMode = 'del'
        else:
            e.ignore()
    
    def dropEvent(self, e):
        if self.dragMode == 'add':
            super(textGer, self).dropEvent(e)
            self.undo()
            Ui.isSqlCalled = True
            Ui.sqlCallCode = 'insertUS-ger'
            Ui.sqlThread.start()
            textGer.isSentenceExisting = True
            R2 = existColor[0]
            G2 = existColor[1]
            B2 = existColor[2]
            R = self.color[0]
            G = self.color[1]
            B = self.color[2]
            self.animation.stop()
            self.animation.setStartValue(QRect(R, G, B, shadowValue))
            self.animation.setEndValue(QRect(R2, G2, B2, shadowValue))
            self.animation.setDuration(slowDuration)
            self.animation.start()
            self.color = [R2, G2, B2, 255]
        elif self.dragMode == 'del':
            super(textGer, self).dropEvent(e)
            self.undo()
            Ui.isSqlCalled = True
            Ui.sqlCallCode = 'delUS-line'
            Ui.sqlThread.start()
            textGer.isSentenceExisting = False
            R2 = notExistColor[0]
            G2 = notExistColor[1]
            B2 = notExistColor[2]
            R = self.color[0]
            G = self.color[1]
            B = self.color[2]
            self.animation.stop()
            self.animation.setStartValue(QRect(R, G, B, shadowValue))
            self.animation.setEndValue(QRect(R2, G2, B2, shadowValue))
            self.animation.setDuration(slowDuration)
            self.animation.start()
            self.color = [R2, G2, B2, 255]


class textEng(QtWidgets.QTextBrowser):
    def __init__(self, parent):
        super(textEng, self).__init__(parent)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setMinimumSize(QtCore.QSize(200, 0))
        self.setTabChangesFocus(True)
        self.setUndoRedoEnabled(True)
        self.setAcceptDrops(True)
        self.setAcceptRichText(False)
        self.setCursorWidth(2)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        textEng.isSentenceExisting = False
        textEng.isThereText = False
        textEng.displayedText = None
        
        self.mouseIn = False
        self.hovering = False
        self.color = blankColor
        self.dragMode = ''
        
        self.animation = QtCore.QVariantAnimation()
        self.animation.valueChanged.connect(self.updateStyle)
        self.textChanged.connect(self.on_textChange)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        Ui.sqlThread.searchEngSignal.connect(self.onSearch)
        Ui.interThread.interCallEngBox.connect(self.on_interCall)
    
    @pyqtSlot('PyQt_PyObject')
    def onSearch(self, result):
        self.clear()
        self.setPlaceholderText('English Box')
        if result != None:
            self.setCursorWidth(0)
            self.setTextInteractionFlags(
                QtCore.Qt.LinksAccessibleByKeyboard |
                QtCore.Qt.LinksAccessibleByMouse |
                QtCore.Qt.TextBrowserInteraction |
                QtCore.Qt.TextEditable |
                QtCore.Qt.TextEditorInteraction |
                QtCore.Qt.TextSelectableByKeyboard |
                QtCore.Qt.TextSelectableByMouse)
            textEng.isSentenceExisting = True
            self.append(result)
            R2 = existColor[0]
            G2 = existColor[1]
            B2 = existColor[2]
        else:
            self.setCursorWidth(2)
            textEng.isSentenceExisting = False
            self.setTextInteractionFlags(
                QtCore.Qt.LinksAccessibleByKeyboard |
                QtCore.Qt.LinksAccessibleByMouse |
                QtCore.Qt.TextBrowserInteraction |
                QtCore.Qt.TextEditable |
                QtCore.Qt.TextEditorInteraction |
                QtCore.Qt.TextSelectableByKeyboard |
                QtCore.Qt.TextSelectableByMouse)
            R2 = notExistColor[0]
            G2 = notExistColor[1]
            B2 = notExistColor[2]
        c = QColor(R2, G2, B2)
        self.shadow.setColor(c)
        self.color = [R2, G2, B2, 255]
    
    @pyqtSlot('PyQt_PyObject')
    def on_interCall(self, code):
        if code == 'hide':
            self.clear()
            self.setPlaceholderText('')
            self.hovering = False
            self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            textEng.isSentenceExisting = False
            textEng.isThereText = False
            textEng.displayedText = None
            self.mouseIn = False
            self.color = blankColor
        if 'paintOn' in code:
            self.setDisabled(True)
            if self.hovering == True:
                self.animationEnd()
                self.hovering = False
        if 'paintOff' in code:
            self.setDisabled(False)
        if 'drag' in code and textEng.isThereText == True:
            if 'add' in code:
                if textEng.isSentenceExisting == False:
                    if self.hovering == True:
                        pass
                    else:
                        self.animationBegin()
                        self.hovering = True
                else:
                    if self.hovering == False:
                        pass
                    else:
                        self.animationEnd()
                        self.hovering = False
            elif 'del' in code:
                if textEng.isSentenceExisting == True:
                    if self.hovering == True:
                        pass
                    else:
                        self.animationBegin()
                        self.hovering = True
                else:
                    if self.hovering == False:
                        pass
                    else:
                        self.animationEnd()
                        self.hovering = False
        if 'reformat' in code:
            textEng.isSentenceExisting = False
            self.setCursorWidth(2)
            R2 = notExistColor[0]
            G2 = notExistColor[1]
            B2 = notExistColor[2]
            if self.hovering == True:
                R = self.color[0]
                G = self.color[1]
                B = self.color[2]
                self.animation.stop()
                self.animation.setStartValue(QRect(R, G, B, shadowValue))
                self.animation.setEndValue(QRect(R2, G2, B2, shadowValue))
                self.animation.setDuration(slowDuration)
                self.animation.start()
            self.color = [R2, G2, B2, 255]
    
    @pyqtSlot()
    def animationEnd(self):
        self.animation.stop()
        self.animation.setStartValue(QPoint(shadowValue, 0))
        self.animation.setEndValue(QPoint(0, 0))
        self.animation.setDuration(slowDuration)
        self.animation.start()
    
    @pyqtSlot()
    def animationBegin(self):
        self.animation.stop()
        self.animation.setStartValue(QPoint(0, 0))
        self.animation.setEndValue(QPoint(shadowValue, 0))
        self.animation.setDuration(slowDuration)
        self.animation.start()
    
    @pyqtSlot(QtCore.QVariant)
    def updateStyle(self, value):
        if type(value) == QPoint:
            self.shadow.setOffset(value.x() / offsetDivide)
        if type(value) == QRect:
            c = QColor(value.x(), value.y(), value.width())
            self.shadow.setColor(c)
            self.shadow.setOffset(value.height() / offsetDivide)
    
    @pyqtSlot()
    def on_textChange(self):
        textEng.displayedText = self.toPlainText()
        if textEng.displayedText.strip() == '' and textEng.isThereText == True:
            textEng.isThereText = False
            if self.hovering == False and textGer.atInsertion == False:
                self.animationBegin()
                timer = QtCore.QTimer()
                timer.singleShot(slowDuration + 50, self.animationEnd)
                self.hovering = False
            else:
                self.animationEnd()
                self.hovering = False
        if textEng.displayedText.strip() != '' and textEng.isThereText == False:
            textEng.isThereText = True
            self.atAnimationBegin = True
            self.hovering = True
            self.animationBegin()
    
    def keyPressEvent(self, event):
        if self.isSentenceExisting == True:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ControlModifier and (event.key() == QtCore.Qt.Key_C or
                                                           event.key() == QtCore.Qt.Key_A):
                super(textEng, self).keyPressEvent(event)
            return
        super(textEng, self).keyPressEvent(event)
    
    def enterEvent(self, event):
        self.mouseIn = True
        if textEng.isThereText == True and self.hovering == False and textGer.isPaintOn == False:
            self.hovering = True
            self.animationBegin()
    
    def leaveEvent(self, event):
        self.mouseIn = False
        if textEng.isThereText == True and textGer.isPaintOn == False and self.hovering == True:
            self.atAnimationBegin = False
            self.hovering = False
            self.animationEnd()
    
    def dragEnterEvent(self, e):
        self.dragMode = ''
        if e.mimeData().data('drag') == b'add' and textEng.isSentenceExisting == False and textEng.isThereText == True:
            e.accept()
            self.dragMode = 'add'
        elif e.mimeData().data('drag') == b'del' and textEng.isSentenceExisting == True and textEng.isThereText == True:
            e.accept()
            self.dragMode = 'del'
        else:
            e.ignore()
    
    def dropEvent(self, e):
        if self.dragMode == 'add':
            super(textEng, self).dropEvent(e)
            self.undo()
            if textGer.isSentenceExisting == True:
                Ui.isSqlCalled = True
                Ui.sqlCallCode = 'updateUS'
                Ui.sqlThread.start()
            
            else:
                Ui.isSqlCalled = True
                Ui.sqlCallCode = 'insertUS-ger-eng'
                Ui.sqlThread.start()
                Ui.interCallTo = 'gerBox'
                Ui.interCallCode = 'updateInsertion'
                Ui.isInterThreadCalled = True
                Ui.interThread.start()
            textEng.isSentenceExisting = True
            R2 = existColor[0]
            G2 = existColor[1]
            B2 = existColor[2]
            R = self.color[0]
            G = self.color[1]
            B = self.color[2]
            self.animation.stop()
            self.animation.setStartValue(QRect(R, G, B, shadowValue))
            self.animation.setEndValue(QRect(R2, G2, B2, shadowValue))
            self.animation.setDuration(slowDuration)
            self.animation.start()
            self.color = [R2, G2, B2, 255]
            self.setCursorWidth(0)
        elif self.dragMode == 'del':
            Ui.isSqlCalled = True
            Ui.sqlCallCode = 'updatUS-noeng'
            Ui.sqlThread.start()
            self.setCursorWidth(2)
            textEng.isSentenceExisting = False
            R2 = notExistColor[0]
            G2 = notExistColor[1]
            B2 = notExistColor[2]
            R = self.color[0]
            G = self.color[1]
            B = self.color[2]
            self.animation.stop()
            self.animation.setStartValue(QRect(R, G, B, shadowValue))
            self.animation.setEndValue(QRect(R2, G2, B2, shadowValue))
            self.animation.setDuration(slowDuration)
            self.animation.start()
            self.color = [R2, G2, B2, 255]
            super(textEng, self).dropEvent(e)
            self.undo()


class searchB(QtWidgets.QLineEdit):
    def __init__(self, parent):
        super(searchB, self).__init__(parent)
        self.setClearButtonEnabled(True)
        
        searchB.isThereText = False
        searchB.displayedText = None
        
        self.textChanged.connect(self.on_textChange)
        Ui.interThread.interCallsearchB.connect(self.on_interCall)
    
    @pyqtSlot('PyQt_PyObject')
    def on_interCall(self, code):
        if 'paintOn' in code:
            self.setDisabled(True)
        if 'paintOff' in code:
            self.setDisabled(False)
    
    @pyqtSlot()
    def on_textChange(self):
        searchB.displayedText = self.text()
        if searchB.displayedText.strip() == '' and searchB.isThereText == True:
            searchB.isThereText = False
        
        if searchB.displayedText.strip() != '' and searchB.isThereText == False:
            searchB.isThereText = True
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return and searchB.isThereText == True:
            Ui.isDictCalled = True
            Ui.dictCallCode = searchB.displayedText.strip()
            Ui.dictThread.start()
        
        super(searchB, self).keyPressEvent(event)


class resultB(QtWidgets.QTextBrowser):
    def __init__(self, parent):
        super(resultB, self).__init__(parent)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setMinimumSize(QtCore.QSize(200, 0))
        self.setUndoRedoEnabled(True)
        self.setAcceptRichText(False)
        self.setCursorWidth(0)
        self.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse |
            QtCore.Qt.TextBrowserInteraction |
            QtCore.Qt.TextEditorInteraction |
            QtCore.Qt.TextSelectableByMouse)
        
        resultB.isWordExisting = False
        resultB.isThereWord = False
        resultB.displayedKeyword = None
        resultB.displayedDict = None
        
        self.color = greyColor
        self.hovering = False
        self.mouseIn = False
        self.animation = QtCore.QVariantAnimation()
        self.animation.valueChanged.connect(self.updateStyle)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(self.color)
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        
        Ui.dictThread.dictResult.connect(self.on_searchResults)
        Ui.dictThread.existsOrNotSignal.connect(self.checkExistance)
        Ui.interThread.interCallresultB.connect(self.on_interCall)
    
    @pyqtSlot('PyQt_PyObject')
    def on_interCall(self, code):
        if code == 'paintErr':
            if self.hovering == False:
                self.animationBegin()
                timer = QtCore.QTimer()
                timer.singleShot(slowDuration, self.animationEnd)
            else:
                self.animationEnd()
                timer = QtCore.QTimer()
                timer.singleShot(slowDuration, self.animationBegin)
        if 'paintOn' in code:
            if self.hovering == True:
                self.hovering = False
                self.animationEnd()
        if 'drag' in code and resultB.isThereWord == True:
            if 'add' in code:
                if resultB.isWordExisting == False:
                    if self.hovering == True:
                        pass
                    else:
                        self.animationBegin()
                        self.hovering = True
                else:
                    if self.hovering == False:
                        pass
                    else:
                        self.animationEnd()
                        self.hovering = False
            elif 'del' in code:
                if resultB.isWordExisting == True:
                    if self.hovering == True:
                        pass
                    else:
                        self.animationBegin()
                        self.hovering = True
                else:
                    if self.hovering == False:
                        pass
                    else:
                        self.animationEnd()
                        self.hovering = False
    
    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    def on_searchResults(self, text1, text2, text3):
        if text1 == 'No Results' or text1 == 'scraper_call_error':
            self.clear()
            resultB.isWordExisting = False
            resultB.isThereWord = False
            variableFormat = QTextCharFormat()
            variableFormat.setFontWeight(QtGui.QFont.Bold)
            variableFormat.setForeground(redColor)
            self.setCurrentCharFormat(variableFormat)
            if text1 == 'No Results':
                self.append(messages[0])
                self.append(dictThread.searchedWord)
            elif text1 == 'scraper_call_error':
                self.append(messages[2])
            if self.hovering == True:
                self.animationEnd()
                self.hovering = False
        if 'blocknum' in text1:
            resultB.isThereWord = True
            if '1' in text1 and resultB.cleared == False:
                self.clear()
                resultB.cleared = True
                self.oldtext1 = text1
            self.newtext1 = text1
            if self.newtext1 != self.oldtext1:
                self.oldtext1 = self.newtext1
                self.append('')
            if text2 == 'wordname':
                variableFormat = QTextCharFormat()
                variableFormat.setFontWeight(QtGui.QFont.Bold)
                variableFormat.setForeground(greenColor)
                self.setCurrentCharFormat(variableFormat)
                self.append(text3)
            if text2 == 'carac':
                variableFormat = QTextCharFormat()
                variableFormat.setForeground(greyColor)
                self.setCurrentCharFormat(variableFormat)
                self.append(text3)
            if text2 == 'phrase':
                variableFormat = QTextCharFormat()
                variableFormat.setFontWeight(QtGui.QFont.Bold)
                variableFormat.setForeground(blueColor)
                self.setCurrentCharFormat(variableFormat)
                self.append('>' + ' ' + text3)
            if text2 == 'gerdef':
                variableFormat = QTextCharFormat()
                variableFormat.setFontWeight(QtGui.QFont.Bold)
                variableFormat.setForeground(purple1Color)
                self.setCurrentCharFormat(variableFormat)
                self.append(text3)
            if text2 == 'engdef':
                variableFormat = QTextCharFormat()
                variableFormat.setFontWeight(QtGui.QFont.Bold)
                variableFormat.setForeground(purple2Color)
                self.setCurrentCharFormat(variableFormat)
                self.setFontItalic(True)
                self.append(text3)
            if text2 == 'exampger':
                variableFormat = QTextCharFormat()
                variableFormat.setFontWeight(QtGui.QFont.Normal)
                variableFormat.setForeground(softBlueColor1)
                self.setCurrentCharFormat(variableFormat)
                self.append(spacingText + text3)
            if text2 == 'exampeng':
                variableFormat = QTextCharFormat()
                variableFormat.setFontWeight(QtGui.QFont.Normal)
                variableFormat.setForeground(softBlueColor2)
                self.setCurrentCharFormat(variableFormat)
                self.setFontItalic(True)
                self.append(spacingText + text3)
    
    @pyqtSlot('PyQt_PyObject')
    def checkExistance(self, code):
        self.moveCursor(QtGui.QTextCursor.Start)
        self.atAnimationBegin = True
        if code == 'yes':
            resultB.isWordExisting = True
            R2 = existColor[0]
            G2 = existColor[1]
            B2 = existColor[2]
            c = QColor(R2, G2, B2)
        if code == 'no':
            resultB.isWordExisting = False
            R2 = notExistColor[0]
            G2 = notExistColor[1]
            B2 = notExistColor[2]
            c = QColor(R2, G2, B2)
        if code == 'changed':
            resultB.isWordExisting = True
            R2 = existColor[0]
            G2 = existColor[1]
            B2 = existColor[2]
            c = QColor(R2, G2, B2)
            variableFormat = QTextCharFormat()
            variableFormat.setFontWeight(QtGui.QFont.Bold)
            variableFormat.setForeground(redColor)
            self.setCurrentCharFormat(variableFormat)
            self.append('')
            self.append(messages[1])
        if self.hovering == False:
            self.preEnter = False
            self.hovering = True
            self.shadow.setColor(c)
            self.color = c
            self.animationBegin()
        elif self.hovering == True:
            self.animation.stop()
            self.animation.setStartValue(self.color)
            self.animation.setEndValue(c)
            self.animation.setDuration(evenSlowerDuration)
            self.animation.start()
            self.color = c
    
    @pyqtSlot()
    def animationEnd(self):
        self.animation.stop()
        self.animation.setStartValue(QPoint(shadowValue, 0))
        self.animation.setEndValue(QPoint(0, 0))
        self.animation.setDuration(slowDuration)
        self.animation.start()
    
    @pyqtSlot()
    def animationBegin(self):
        self.animation.stop()
        self.animation.setStartValue(QPoint(0, 0))
        self.animation.setEndValue(QPoint(shadowValue, 0))
        self.animation.setDuration(slowDuration)
        self.animation.start()
    
    @pyqtSlot(QtCore.QVariant)
    def updateStyle(self, value):
        if type(value) == QPoint:
            self.shadow.setOffset(value.x() / offsetDivide)
        if type(value) == QRect:
            c = QColor(value.x(), value.y(), value.width())
            self.shadow.setColor(c)
            self.shadow.setOffset(value.height() / offsetDivide)
        if type(value) == QColor:
            c = QColor(value.red(), value.green(), value.blue())
            self.shadow.setColor(c)
    
    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier and (event.key() == QtCore.Qt.Key_C or
                                                       event.key() == QtCore.Qt.Key_A):
            super().keyPressEvent(event)
        return
    
    def enterEvent(self, event):
        self.mouseIn = True
        if resultB.isThereWord == True and self.hovering == False and textGer.isPaintOn == False:
            self.hovering = True
            self.animationBegin()
        if resultB.isThereWord == False:
            self.preEnter = True
        else:
            self.preEnter = False
    
    def leaveEvent(self, event):
        self.mouseIn = False
        if resultB.isThereWord == True and textGer.isPaintOn == False and self.hovering == True:
            self.atAnimationBegin = False
            self.hovering = False
            self.animationEnd()
        self.preEnter = False
    
    def dragEnterEvent(self, e):
        self.dragMode = ''
        if e.mimeData().data('drag') == b'add' and resultB.isWordExisting == False and resultB.isThereWord == True:
            e.accept()
            self.dragMode = 'add'
        elif e.mimeData().data('drag') == b'del' and resultB.isWordExisting == True and resultB.isThereWord == True:
            e.accept()
            self.dragMode = 'del'
        else:
            e.ignore()
    
    def dropEvent(self, e):
        if self.dragMode == 'add':
            Ui.isSqlCalled = True
            Ui.sqlCallCode = 'insertUW'
            Ui.sqlThread.start()
            resultB.isWordExisting = True
            R2 = existColor[0]
            G2 = existColor[1]
            B2 = existColor[2]
            c = QColor(R2, G2, B2)
            self.animation.stop()
            self.animation.setStartValue(self.color)
            self.animation.setEndValue(c)
            self.animation.setDuration(slowDuration)
            self.animation.start()
            self.color = c
        elif self.dragMode == 'del':
            Ui.isSqlCalled = True
            Ui.sqlCallCode = 'delUW'
            Ui.sqlThread.start()
            resultB.isWordExisting = False
            R2 = notExistColor[0]
            G2 = notExistColor[1]
            B2 = notExistColor[2]
            c = QColor(R2, G2, B2)
            self.animation.stop()
            self.animation.setStartValue(self.color)
            self.animation.setEndValue(c)
            self.animation.setDuration(slowDuration)
            self.animation.start()
            self.color = c


class removeP(QtWidgets.QPushButton):
    def __init__(self, parent):
        super(removeP, self).__init__(parent)
        self.setMinimumSize(QtCore.QSize(50, 50))
        self.setMaximumSize(QtCore.QSize(50, 50))
        
        addP.isPaintDelOn = False
        addP.isDelPressAvailable = False
        removeP.buttonState = 0
        
        self.clicked.connect(self.on_click)
    
    @pyqtSlot()
    def on_click(self):
        if removeP.buttonState == 0 and textGer.manifestations != []:
            removeP.buttonState = 1
            Ui.interCallTo = 'searchB-engBox-gerBox-resultB'
            Ui.interCallCode = 'paintOn-del'
            Ui.isInterThreadCalled = True
            Ui.interThread.start()
            textGer.isPaintOn = True
            textGer.paintMode = 'del'
        elif removeP.buttonState == 1:
            if textGer.paintAddStr != '':
                temp = copy.deepcopy(textGer.manifestations)
                for x, el in enumerate(temp):
                    if el in textGer.paintAddStr:
                        textGer.manifestations.remove(el)
                    elif '-' in el:
                        sublist = el.split('-')
                        newel = ''
                        for subel in sublist:
                            if subel not in textGer.paintAddStr:
                                newel = newel + '-' + subel
                        if newel == '':
                            textGer.manifestations.remove(el)
                        else:
                            newel = newel[1:]
                            textGer.manifestations[x] = newel
                Ui.isSqlCalled = True
                Ui.sqlCallCode = 'delUS_UW'
                Ui.sqlThread.start()
            
            Ui.interCallTo = 'searchB-engBox-gerBox'
            Ui.interCallCode = 'paintOff'
            Ui.isInterThreadCalled = True
            Ui.interThread.start()
            textGer.isPaintOn = False
            textGer.paintMode = ''
            removeP.buttonState = 0
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pass
        super(removeP, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton and textGer.isPaintOn == False and (
                textGer.isInserted == True or resultB.isThereWord == True
        ):
            Ui.interCallTo = 'engBox-gerBox-resultB'
            Ui.interCallCode = 'drag-del'
            Ui.isInterThreadCalled = True
            Ui.interThread.start()
            hotSpot = event.pos()
            mimeData = QMimeData()
            mimeData.setText(' ')
            mimeData.setData('drag', b'del')
            
            pixmap = QPixmap()
            pixmap.load(":/icons/rsc/can50.png")
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(hotSpot)
            
            acceptDropCursor = QPixmap(":/icons/rsc/checkmark50.png")
            acceptDropCursor = acceptDropCursor.scaled(30, 30, transformMode=QtCore.Qt.SmoothTransformation)
            ignoreDropCursor = QPixmap(":/icons/rsc/delete50.png")
            ignoreDropCursor = ignoreDropCursor.scaled(30, 30, transformMode=QtCore.Qt.SmoothTransformation)
            drag.setDragCursor(ignoreDropCursor, Qt.IgnoreAction)
            drag.setDragCursor(acceptDropCursor, Qt.MoveAction)
            drag.exec_()
        
        super(removeP, self).mouseMoveEvent(event)


class addP(QtWidgets.QPushButton):
    def __init__(self, parent):
        super(addP, self).__init__(parent)
        self.setMinimumSize(QtCore.QSize(50, 50))
        self.setMaximumSize(QtCore.QSize(50, 50))
        
        addP.isPaintAddOn = False
        addP.isAddPressAvailable = False
        addP.buttonState = 0
        
        self.clicked.connect(self.on_click)
    
    @pyqtSlot()
    def on_click(self):
        Ui.interCallTo = ''
        if addP.buttonState == 0 and textGer.isSentenceExisting == False and textGer.isThereSentence == True:
            Ui.interCallTo = Ui.interCallTo + 'gerBox-'
        if addP.buttonState == 0 and resultB.isWordExisting == False and resultB.isThereWord == True:
            Ui.interCallTo = Ui.interCallTo + 'resultB'
        if Ui.interCallTo != '':
            Ui.interCallCode = 'paintErr'
            Ui.isInterThreadCalled = True
            Ui.interThread.start()
        if addP.buttonState == 0 and textGer.isSentenceExisting == True and resultB.isWordExisting == True:
            addP.buttonState = 1
            Ui.interCallTo = 'searchB-engBox-gerBox-resultB'
            Ui.interCallCode = 'paintOn-add'
            Ui.isInterThreadCalled = True
            Ui.interThread.start()
            textGer.isPaintOn = True
            textGer.paintMode = 'add'
        elif addP.buttonState == 1:
            if textGer.paintAddStr != '':
                Ui.isSqlCalled = True
                Ui.sqlCallCode = 'insertUS_UW'
                Ui.sqlThread.start()
                textGer.manifestations.append(textGer.paintAddStr)
            Ui.interCallTo = 'searchB-engBox-gerBox'
            Ui.interCallCode = 'paintOff'
            Ui.isInterThreadCalled = True
            Ui.interThread.start()
            textGer.isPaintOn = False
            textGer.paintMode = ''
            addP.buttonState = 0
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pass
        super(addP, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton and textGer.isPaintOn == False and (
                textGer.isInserted == True or resultB.isThereWord == True
        ):
            Ui.interCallTo = 'engBox-gerBox-resultB'
            Ui.interCallCode = 'drag-add'
            Ui.isInterThreadCalled = True
            Ui.interThread.start()
            hotSpot = event.pos()
            mimeData = QMimeData()
            mimeData.setText(' ')
            mimeData.setData('drag', b'add')
            
            pixmap = QPixmap()
            pixmap.load(":/icons/rsc/can.png")
            
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(hotSpot)
            
            acceptDropCursor = QPixmap(":/icons/rsc/checkmark50.png")
            acceptDropCursor = acceptDropCursor.scaled(30, 30, transformMode=QtCore.Qt.SmoothTransformation)
            ignoreDropCursor = QPixmap(":/icons/rsc/delete50.png")
            ignoreDropCursor = ignoreDropCursor.scaled(30, 30, transformMode=QtCore.Qt.SmoothTransformation)
            drag.setDragCursor(ignoreDropCursor, Qt.IgnoreAction)
            drag.setDragCursor(acceptDropCursor, Qt.MoveAction)
            drag.exec_()
        
        super(addP, self).mouseMoveEvent(event)


class Ui(object):
    def setupUi(self, MainWindow):
        Ui.interThread = interThread()
        Ui.sqlThread = sqlThread()
        Ui.sqlThreadFinished = True
        Ui.dictThread = dictThread()
        
        Ui.isInterThreadCalled = False
        Ui.isSqlCalled = False
        Ui.sqlCallCode = None
        Ui.isDictCalled = False
        Ui.dictCallCode = None
        Ui.interCallTo = None
        Ui.interCallCode = None
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(878, 552)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        MainWindow.setStyleSheet(mainStyleSheet)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo/wml2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSpacing(5)
        self.logoLabel = label(self.centralwidget)
        self.logoLabel.setObjectName("logoLabel")
        self.gridLayout.addWidget(self.logoLabel, 0, 0, 1, 1)
        self.splitH = QtWidgets.QSplitter(self.centralwidget)
        self.splitH.setOrientation(QtCore.Qt.Horizontal)
        self.splitH.setHandleWidth(10)
        self.splitH.setChildrenCollapsible(False)
        self.splitH.setObjectName("splitH")
        self.splitV = QtWidgets.QSplitter(self.splitH)
        self.splitV.setOrientation(QtCore.Qt.Vertical)
        self.splitV.setHandleWidth(10)
        self.splitV.setChildrenCollapsible(False)
        self.splitV.setObjectName("splitV")
        self.senBox = textGer(self.splitV)
        self.senBox.setObjectName("senBox")
        self.engBox = textEng(self.splitV)
        self.engBox.setObjectName("engBox")
        self.layoutWidget = QtWidgets.QWidget(self.splitH)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 5, 0)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.searchBox = searchB(self.layoutWidget)
        self.searchBox.setObjectName("searchBox")
        self.verticalLayout.addWidget(self.searchBox)
        self.resultBox = resultB(self.layoutWidget)
        self.resultBox.setObjectName("resultBox")
        self.verticalLayout.addWidget(self.resultBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.plusButton = addP(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plusButton.sizePolicy().hasHeightForWidth())
        self.plusButton.setSizePolicy(sizePolicy)
        self.plusButton.setObjectName("plusButton")
        self.horizontalLayout.addWidget(self.plusButton)
        self.minusButton = removeP(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.minusButton.sizePolicy().hasHeightForWidth())
        self.minusButton.setSizePolicy(sizePolicy)
        self.minusButton.setObjectName("minusButton")
        self.horizontalLayout.addWidget(self.minusButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addWidget(self.splitH, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 878, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle('Wanderlust by Wael Mcharek (Beta)')
        self.logoLabel.setText(_translate("MainWindow", "TextLabel"))
        self.senBox.setPlaceholderText(_translate("MainWindow", "sentence box"))
        self.searchBox.setPlaceholderText(_translate("MainWindow", "search"))
        self.resultBox.setPlaceholderText(_translate("MainWindow", "results"))
        self.plusButton.setText(_translate("MainWindow", "+"))
        self.minusButton.setText(_translate("MainWindow", "-"))


class splashScr(QSplashScreen):
    def __init__(self, parent=None):
        super().__init__()
        self.app = parent
        self.setPixmap(QPixmap(":/bg/splash2.png"))
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
    
    def showEvent(self, event):
        self.display()
        super().showEvent(event)
    
    def display(self):
        self.app.processEvents()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = splashScr(app)
    splash.show()
    
    dt = data()
    DT = Data()
    
    qd = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    qd.setDatabaseName('data.db')
    qd.open()
    query = QtSql.QSqlQuery()
    
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui()
    ui.setupUi(MainWindow)
    MainWindow.show()
    splash.finish(MainWindow)
    sys.exit(app.exec_())