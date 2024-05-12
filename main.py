import datetime
import os

from core import ReportManager, reverseDict, DXA
from gui import QtWidgets, Ui_ReportGenerator, QtCore
from dialog import Ui_newReportDialog
import sys

months = {
    'Januar': 1,
    'Februar': 2,
    'Mart': 3,
    'April': 4,
    'Maj': 5,
    'Jul': 6,
    'Jun': 7,
    'Avgust': 8,
    'Septembar': 9,
    'Oktobar': 10,
    'Novembar': 11,
    'Decembar': 12
}


def decodeSelectedReportFromList(report: str) -> dict:
    return {
        'reportType': report.split('-')[0],
        'month': int(report.split('-')[1].split('/')[0]),
        'year': int(report.split('-')[1].split('/')[1])
    }


def enableInput(mainUI: Ui_ReportGenerator, reportType: int):
    mainUI.deleteReportBtn.setEnabled(True)
    mainUI.inputName.setEnabled(True)
    mainUI.dateInput.setEnabled(True)
    mainUI.inputSurname.setEnabled(True)
    mainUI.comboStatusInput.setEnabled(True)
    mainUI.addPatientBtn.setEnabled(True)
    mainUI.saveReportBtn.setEnabled(True)
    mainUI.generateXLSXBtn.setEnabled(True)
    if reportType == 0:
        mainUI.comboNurseInput.setEnabled(True)
        mainUI.comboDoctorInput.setEnabled(True)


def disableInput(mainUI: Ui_ReportGenerator):
    mainUI.deleteReportBtn.setEnabled(False)
    mainUI.deletePatientBtn.setEnabled(False)
    mainUI.saveReportBtn.setEnabled(False)
    mainUI.generateXLSXBtn.setEnabled(False)
    mainUI.addPatientBtn.setEnabled(False)
    mainUI.inputName.setEnabled(False)
    mainUI.inputName.setText('')
    mainUI.dateInput.setEnabled(False)
    mainUI.inputSurname.setEnabled(False)
    mainUI.inputSurname.setText('')
    mainUI.comboStatusInput.setEnabled(False)
    mainUI.comboNurseInput.setEnabled(False)
    mainUI.comboDoctorInput.setEnabled(False)


def fillInputData(mainUI: Ui_ReportGenerator, reportManager: ReportManager):
    reportStr = mainUI.listOfReports.currentItem()
    if reportStr is None:
        disableInput(mainUI=mainUI)
        mainUI.comboStatusInput.clear()
        mainUI.comboDoctorInput.clear()
        mainUI.comboNurseInput.clear()
    else:
        reportParts = decodeSelectedReportFromList(reportStr.text())
        report = reportManager.getReport(reportParts['month'], reportParts['year'],
                                         0 if reportParts['reportType'] == 'DXA' else 1)
        for s in report.statusMap.keys():
            mainUI.comboStatusInput.addItem(s)
        if isinstance(report, DXA):
            for d in report.doctorsMap.keys():
                mainUI.comboDoctorInput.addItem(d)
            for n in report.nursesMap.keys():
                mainUI.comboNurseInput.addItem(n)


def checkSelected(mainUI: Ui_ReportGenerator):
    reportStr = mainUI.listOfReports.currentItem()
    if reportStr is None:
        disableInput(mainUI=mainUI)
    else:
        report = decodeSelectedReportFromList(reportStr.text())
        enableInput(mainUI=mainUI, reportType=0 if report['reportType'] == 'DXA' else 1)


def displayTable(reportManager: ReportManager, mainUI: Ui_ReportGenerator):
    mainUI.tableOfPatients.clear()
    mainUI.tableOfPatients.setColumnCount(0)
    mainUI.tableOfPatients.setRowCount(0)
    reportStr = mainUI.listOfReports.currentItem().text()
    reportParts = decodeSelectedReportFromList(reportStr)
    if reportParts['reportType'] == 'DXA':
        mainUI.tableOfPatients.setColumnCount(6)
        column_headers = ['Datum', 'Prezime', 'Ime', 'Odeljenje', 'Lekar', 'Sestra/Tehničar']
        mainUI.tableOfPatients.setHorizontalHeaderLabels(column_headers)
    elif reportParts['reportType'] == 'ABPM':
        mainUI.tableOfPatients.setColumnCount(4)
        column_headers = ['Datum', 'Prezime', 'Ime', 'Odeljenje']
        mainUI.tableOfPatients.setHorizontalHeaderLabels(column_headers)

    report = reportManager.getReport(reportParts['month'], reportParts['year'],
                                     0 if reportParts['reportType'] == 'DXA' else 1)
    row = 0

    for p in report.patients:
        mainUI.tableOfPatients.insertRow(row)
        date = QtWidgets.QTableWidgetItem(f'{p.dt.day}-{p.dt.month}-{p.dt.year}')
        date.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        mainUI.tableOfPatients.setItem(row, 0, date)
        surname = QtWidgets.QTableWidgetItem(p.surname)
        surname.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        mainUI.tableOfPatients.setItem(row, 1, surname)
        name = QtWidgets.QTableWidgetItem(p.name)
        name.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        mainUI.tableOfPatients.setItem(row, 2, name)
        status = QtWidgets.QTableWidgetItem(reverseDict(report.statusMap)[p.status])
        status.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        mainUI.tableOfPatients.setItem(row, 3, status)
        if isinstance(report, DXA):
            doctor = QtWidgets.QTableWidgetItem(reverseDict(report.doctorsMap)[p.doctor])
            doctor.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            mainUI.tableOfPatients.setItem(row, 4, doctor)
            nurse = QtWidgets.QTableWidgetItem(reverseDict(report.nursesMap)[p.nurse])
            nurse.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            mainUI.tableOfPatients.setItem(row, 5, nurse)
        row += 1


def newReport(reportManager: ReportManager, mainUI: Ui_ReportGenerator, dialogUI: Ui_newReportDialog):
    month = months[dialogUI.comboMonthInput.currentText()]
    year = dialogUI.yearInput.value()
    reportType = 0 if dialogUI.radioBtnDXA.isChecked() else 1
    reportManager.create(month, year, reportType)
    item = QtWidgets.QListWidgetItem(f'{"DXA" if reportType == 0 else "ABPM"}-{month}/{year}')
    mainUI.listOfReports.addItem(item)
    mainUI.listOfReports.setCurrentItem(item)
    displayTable(reportManager, mainUI)
    mainUI.listOfReports.clicked.connect(lambda: displayTable(reportManager, mainUI))
    checkSelected(mainUI=mainUI)
    fillInputData(mainUI=mainUI, reportManager=reportManager)


def fillUpData(mainUI: Ui_ReportGenerator, dialogUI: Ui_newReportDialog):
    for key, val in months.items():
        dialogUI.comboMonthInput.addItem(key)
    dialogUI.yearInput.setValue(QtCore.QDate.currentDate().year())
    mainUI.dateInput.setDate(QtCore.QDate.currentDate())


def addNewPatient(mainUI: Ui_ReportGenerator, reportManager: ReportManager):
    reportStr = mainUI.listOfReports.currentItem()
    if reportStr is not None and mainUI.inputName.text() != '' and mainUI.inputSurname.text() != '':
        reportParts = decodeSelectedReportFromList(reportStr.text())
        report = reportManager.getReport(reportParts['month'], reportParts['year'],
                                         0 if reportParts['reportType'] == 'DXA' else 1)
        report.addPatient(mainUI.dateInput.date().toPyDate(),
                          mainUI.inputName.text(),
                          mainUI.inputSurname.text(),
                          mainUI.comboStatusInput.currentText(),
                          mainUI.comboDoctorInput.currentText() if isinstance(report, DXA) else None,
                          mainUI.comboNurseInput.currentText() if isinstance(report, DXA) else None
                          )
        row = mainUI.tableOfPatients.rowCount()
        mainUI.tableOfPatients.insertRow(row)
        date = QtWidgets.QTableWidgetItem(
            f'{mainUI.dateInput.date().day()}-{mainUI.dateInput.date().month()}-{mainUI.dateInput.date().year()}')
        date.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        mainUI.tableOfPatients.setItem(row, 0, date)
        surname = QtWidgets.QTableWidgetItem(mainUI.inputSurname.text())
        surname.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        mainUI.tableOfPatients.setItem(row, 1, surname)
        name = QtWidgets.QTableWidgetItem(mainUI.inputName.text())
        name.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        mainUI.tableOfPatients.setItem(row, 2, name)
        status = QtWidgets.QTableWidgetItem(mainUI.comboStatusInput.currentText())
        status.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        mainUI.tableOfPatients.setItem(row, 3, status)
        if isinstance(report, DXA):
            doctor = QtWidgets.QTableWidgetItem(mainUI.comboDoctorInput.currentText())
            doctor.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            mainUI.tableOfPatients.setItem(row, 4, doctor)
            nurse = QtWidgets.QTableWidgetItem(mainUI.comboNurseInput.currentText())
            nurse.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            mainUI.tableOfPatients.setItem(row, 5, nurse)


def clearTable(mainUI: Ui_ReportGenerator):
    mainUI.tableOfPatients.clear()


def deleteSelectedReport(reportManager: ReportManager, mainUI: Ui_ReportGenerator):
    reportStr = mainUI.listOfReports.currentItem()
    if reportStr is not None:
        mainUI.listOfReports.takeItem(mainUI.listOfReports.currentRow())
        mainUI.tableOfPatients.clear()
        mainUI.tableOfPatients.setColumnCount(0)
        mainUI.tableOfPatients.setRowCount(0)
        reportParts = decodeSelectedReportFromList(reportStr.text())
        reportManager.delete(reportParts['month'], reportParts['year'], 0 if reportParts['reportType'] == 'DXA' else 1)
        checkSelected(mainUI)


def saveReport(reportManager: ReportManager, mainUI: Ui_ReportGenerator):
    reportStr = mainUI.listOfReports.currentItem()
    if reportStr is not None:
        reportParts = decodeSelectedReportFromList(reportStr.text())
        fileExt = f"{'DXA (*.dxa)' if reportParts['reportType'] == 'DXA' else 'ABPM (*.apbm)'}"
        filePath, ext = QtWidgets.QFileDialog.getSaveFileName(caption='Sačuvaj izveštaj: ', directory=os.getcwd(),
                                                              filter=fileExt)
        if filePath != '':
            reportManager.getReport(reportParts['month'], reportParts['year'],
                                    0 if reportParts['reportType'] == 'DXA' else 1).save(filePath)


def loadReport(reportManager: ReportManager, mainUI: Ui_ReportGenerator):
    fileExt = "DXA (*.dxa);;ABPM (*.apbm)"
    filePath, ext = QtWidgets.QFileDialog.getOpenFileName(caption='Učitaj izveštaj: ', directory=os.getcwd(),
                                                          filter=fileExt)
    if filePath != '':
        report = reportManager.load(filePath)
        if isinstance(report, str):
            pass
            # todo error print
        elif report is not None:
            item = QtWidgets.QListWidgetItem(
                f'{"DXA" if isinstance(report, DXA) else "ABPM"}-{report.month}/{report.year}')
            mainUI.listOfReports.addItem(item)
            mainUI.listOfReports.setCurrentItem(item)
            displayTable(reportManager, mainUI)
            fillInputData(mainUI, reportManager)
            checkSelected(mainUI)


def generateXLSX(reportManager: ReportManager, mainUI: Ui_ReportGenerator):
    reportStr = mainUI.listOfReports.currentItem()
    if reportStr is not None:
        reportParts = decodeSelectedReportFromList(reportStr.text())
        fileExt = "{XLSX (*.xlsx)"
        filePath, ext = QtWidgets.QFileDialog.getSaveFileName(caption='Generiši xlsx izveštaj: ', directory=os.getcwd(),
                                                              filter=fileExt)
        if filePath != '':
            reportManager.getReport(reportParts['month'], reportParts['year'],
                                    0 if reportParts['reportType'] == 'DXA' else 1).exportToXLSX(filePath)


def deleteSelectedPatient(reportManager: ReportManager, mainUI: Ui_ReportGenerator):
    row = mainUI.tableOfPatients.currentRow()
    if row is not None and row >= 0:
        mainUI.tableOfPatients.removeRow(row)
        reportStr = mainUI.listOfReports.currentItem().text()
        reportParts = decodeSelectedReportFromList(reportStr)
        report = reportManager.getReport(reportParts['month'], reportParts['year'], 0 if reportParts['reportType'] == 'DXA' else 1)
        report.removePatientByIndex(row)
        mainUI.deletePatientBtn.setEnabled(False)


def configure(reportManager: ReportManager, mainUI: Ui_ReportGenerator, dialogUI: Ui_newReportDialog):
    fillUpData(mainUI, dialogUI)
    mainUI.createNewBtn.clicked.connect(dialogUI.newReportDialog.show)
    mainUI.addPatientBtn.clicked.connect(lambda: addNewPatient(mainUI=mainUI, reportManager=reportManager))
    mainUI.deleteReportBtn.clicked.connect(lambda: deleteSelectedReport(mainUI=mainUI, reportManager=reportManager))
    mainUI.saveReportBtn.clicked.connect(lambda: saveReport(mainUI=mainUI, reportManager=reportManager))
    mainUI.loadReportBtn.clicked.connect(lambda: loadReport(mainUI=mainUI, reportManager=reportManager))
    mainUI.generateXLSXBtn.clicked.connect(lambda: generateXLSX(mainUI=mainUI, reportManager=reportManager))
    mainUI.deletePatientBtn.clicked.connect(lambda: deleteSelectedPatient(mainUI=mainUI, reportManager=reportManager))
    dialogUI.buttonBox.accepted.connect(lambda: newReport(reportManager, mainUI, dialogUI))

    checkSelected(mainUI=mainUI)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ReportGenerator = QtWidgets.QMainWindow()
    InputDialog = QtWidgets.QDialog()
    InputDialog.setModal(True)
    dialogUI = Ui_newReportDialog()
    dialogUI.setupUi(InputDialog)
    mainUI = Ui_ReportGenerator()
    mainUI.setupUi(ReportGenerator)
    reportManager = ReportManager()
    configure(reportManager, mainUI, dialogUI)
    ReportGenerator.show()
    sys.exit(app.exec_())
