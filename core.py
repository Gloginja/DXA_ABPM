import json
import traceback

import xlsxwriter
from datetime import date, datetime

doctors = []
nurses = []
statuses = []
mapStatusDesc = {}


def importData():
    global statuses
    doctors_f = open('res/doktori.txt', mode='r', encoding='utf-8')
    nurses_f = open('res/sestre.txt', mode='r', encoding='utf-8')
    statuses_f = open('res/statusi.txt', mode='r', encoding='utf-8')
    doctors.extend(doctors_f.read().splitlines())
    doctors_f.close()
    nurses.extend(nurses_f.read().splitlines())
    nurses_f.close()
    for line in statuses_f:
        if ':' in line:
            status, desc = line.split(':')
            statuses.append(status)
            mapStatusDesc[status] = desc.replace('\n', '')
        else:
            statuses.append(line.replace('\n', ''))
    statuses_f.close()


def reverseDict(d: dict) -> dict:
    reversed_dict = {}
    for key, value in d.items():
        reversed_dict[value] = key
    return reversed_dict


def mapMonth(month: int):
    match month:
        case 1:
            return 'januar'
        case 2:
            return 'februar'
        case 3:
            return 'mart'
        case 4:
            return 'april'
        case 5:
            return 'maj'
        case 6:
            return 'jun'
        case 7:
            return 'jul'
        case 8:
            return 'avgust'
        case 9:
            return 'septembar'
        case 10:
            return 'oktobar'
        case 11:
            return 'nobembar'
        case 12:
            return 'decembar'


class Patient:

    def __init__(self, dt: date, name: str, surname: str, status: int, doctor: int | None, nurse: int | None):
        self.dt: date = dt
        self.name: str = name
        self.surname: str = surname
        self.status: int = status
        self.doctor: int | None = doctor
        self.nurse: int | None = nurse

    def toDict(self) -> dict:
        return {
            'date': self.dt.strftime('%d/%m/%Y'),
            'name': self.name,
            'surname': self.surname,
            'status': self.status,
            'doctor': self.doctor,
            'nurse': self.nurse
        }


class Report:
    def __init__(self, month: int, year: int):
        self.month: int = month
        self.year: int = year
        self.patients = list()
        self.statusMap = dict()
        self.statusNumOfPatients = dict()

    def addPatient(self, dt: date, name: str, surname: str, status: str, doctor: str | None, nurse: str | None):
        pass

    def save(self, filePath: str):
        pass

    def load(self, filePath: str):
        pass

    def exportToXLSX(self, filePath: str):
        pass

    def removePatientByIndex(self, index: int):
        pass


class DXA(Report):

    def __init__(self, month: int, year: int):
        super().__init__(month=month, year=year)
        self.doctorsMap = dict()
        self.nursesMap = dict()
        self.doctorsNumOfPatients = dict()
        self.nursesNumOfPatients = dict()
        self.statusNumOfPatients = dict()
        self.mapWorkersAndInit()

    def mapWorkersAndInit(self):
        for i in range(len(doctors)):
            self.doctorsMap[doctors[i]] = str(i)
            self.doctorsNumOfPatients[str(i)] = 0

        for i in range(len(nurses)):
            self.nursesMap[nurses[i]] = str(i)
            self.nursesNumOfPatients[str(i)] = 0

        for i in range(len(statuses)):
            self.statusMap[statuses[i]] = str(i)
            self.statusNumOfPatients[str(i)] = 0

    def addPatient(self, dt: date, name: str, surname: str, status: str, doctor: str, nurse: str):
        mappedDoctor: int = self.doctorsMap[doctor]
        mappedNurse: int = self.nursesMap[nurse]
        mappedStatus: int = self.statusMap[status]
        self.patients.append(Patient(dt=dt,
                                     name=name,
                                     surname=surname,
                                     status=mappedStatus,
                                     doctor=mappedDoctor,
                                     nurse=mappedNurse))
        self.doctorsNumOfPatients[mappedDoctor] = self.doctorsNumOfPatients[mappedDoctor] + 1
        self.nursesNumOfPatients[mappedNurse] = self.nursesNumOfPatients[mappedNurse] + 1
        self.statusNumOfPatients[mappedStatus] = self.statusNumOfPatients[mappedStatus] + 1

    def removePatientByIndex(self, index: int):
        patient: Patient = self.patients.pop(index)
        self.doctorsNumOfPatients[patient.doctor] = self.doctorsNumOfPatients[patient.doctor] - 1
        self.nursesNumOfPatients[patient.nurse] = self.nursesNumOfPatients[patient.nurse] - 1
        self.statusNumOfPatients[patient.status] = self.statusNumOfPatients[patient.status] - 1

    def save(self, filePath: str):
        file = open(filePath, 'w')
        serializablePatients = [p.toDict() for p in self.patients]
        jsonSave = {
            'month': self.month,
            'year': self.year,
            'doctorsMap': self.doctorsMap,
            'nursesMap': self.nursesMap,
            'statusesMap': self.statusMap,
            'doctorsNumOfPatients': self.doctorsNumOfPatients,
            'nursesNumOfPatients': self.nursesNumOfPatients,
            'statusNumOfPatients': self.statusNumOfPatients,
            'patients': serializablePatients
        }
        json.dump(jsonSave, file)
        file.close()

    def load(self, filePath: str):
        file = open(filePath, 'r')
        jsonLoad = json.load(file)
        file.close()
        self.month = jsonLoad['month']
        self.year = jsonLoad['year']
        self.doctorsMap = jsonLoad['doctorsMap']
        self.nursesMap = jsonLoad['nursesMap']
        self.statusMap = jsonLoad['statusesMap']
        self.doctorsNumOfPatients = jsonLoad['doctorsNumOfPatients']
        self.nursesNumOfPatients = jsonLoad['nursesNumOfPatients']
        self.statusNumOfPatients = jsonLoad['statusNumOfPatients']
        self.patients = []
        for p in jsonLoad['patients']:
            self.patients.append(Patient(dt=datetime.strptime(p['date'], '%d/%m/%Y').date(),
                                         name=p['name'],
                                         surname=p['surname'],
                                         status=p['status'],
                                         doctor=p['doctor'],
                                         nurse=p['nurse']))

    def exportToXLSX(self, filePath: str):
        workbook = xlsxwriter.Workbook(filePath)
        worksheet = workbook.add_worksheet(mapMonth(self.month).upper())
        header_format1 = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'vcenter',
            'center_across': 'true',
            'bold': 'true',
            'font_size': 11
        })

        header_format2 = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'vcenter',
            'center_across': 'true',
            'bold': 'true',
            'font_size': 14
        })

        data_format = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'vcenter',
            'center_across': 'true',
            'font_size': 11
        })

        date_format = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'vcenter',
            'center_across': 'true',
            'font_size': 11,
            'num_format': 'd.m.yyyy'
        })

        worksheet.merge_range(0, 0, 1, 12,
                              'ODSEK ZA ENDOKRINOLOGIJU KARDIOVASKULARNOG SISTEMA I OSTEODENZITOMETRIJU',
                              header_format1)
        worksheet.merge_range(2, 0, 3, 12,
                              f'MESEČNI IZVEŠTAJ ZA {mapMonth(self.month).upper()} {self.year} DXA',
                              header_format2)

        worksheet.merge_range(4, 0, 5, 0, 'Datum', header_format1)
        worksheet.merge_range(4, 1, 5, 3, 'Prezime i ime pacijenta', header_format1)
        worksheet.merge_range(4, 4, 5, 4, 'Status', header_format1)
        worksheet.merge_range(4, 5, 5, 8, 'Lekar', header_format1)
        worksheet.merge_range(4, 9, 5, 12, 'Medicinska sestra-tehničar', header_format1)
        currentRow = 6

        reverseMapStatus = reverseDict(self.statusMap)
        reverseMapDoctor = reverseDict(self.doctorsMap)
        reverseMapNurse = reverseDict(self.nursesMap)

        for patient in self.patients:
            worksheet.write_datetime(currentRow, 0, patient.dt, date_format)
            worksheet.merge_range(currentRow, 1, currentRow, 3, f'{patient.surname} {patient.name}', data_format)
            worksheet.write_string(currentRow, 4, reverseMapStatus[patient.status], data_format)
            worksheet.merge_range(currentRow, 5, currentRow, 8, reverseMapDoctor[patient.doctor], data_format)
            worksheet.merge_range(currentRow, 9, currentRow, 12, reverseMapNurse[patient.nurse], data_format)
            currentRow += 1

        doctorSumNumPatients = 0
        nurseSumNumPatients = 0

        docs = {}
        nurs = {}
        s = {}

        for doc, num in self.doctorsNumOfPatients.items():
            if num != 0:
                docs[reverseMapDoctor[doc]] = num
                doctorSumNumPatients += num

        for nur, num in self.nursesNumOfPatients.items():
            if num != 0:
                nurs[reverseMapNurse[nur]] = num
                nurseSumNumPatients += num

        for stat, num in self.statusNumOfPatients.items():
            if num != 0:
                s[reverseMapStatus[stat]] = num

        if (len(docs) + len(nurs) + 3) < 60 - currentRow % 60:
            currentRow += 2
        else:
            currentRow += 60 - currentRow % 60

        worksheet.merge_range(currentRow, 0, currentRow, 2, 'Ukupan broj pacijenata', header_format1)
        worksheet.write_number(currentRow, 3, doctorSumNumPatients, header_format1)

        rowForStatuses = currentRow
        currentRow += 1

        for doc, num in docs.items():
            worksheet.merge_range(currentRow, 0, currentRow, 2, doc, data_format)
            worksheet.write_number(currentRow, 3, num, data_format)
            currentRow += 1

        currentRow += 1

        worksheet.merge_range(currentRow, 0, currentRow, 2, 'Ukupan broj pacijenata', header_format1)
        worksheet.write_number(currentRow, 3, nurseSumNumPatients, header_format1)

        currentRow += 1

        for nur, num in nurs.items():
            worksheet.merge_range(currentRow, 0, currentRow, 2, nur, data_format)
            worksheet.write_number(currentRow, 3, num, data_format)
            currentRow += 1

        for st, num in s.items():
            worksheet.write_string(rowForStatuses, 5, st, data_format)
            worksheet.merge_range(rowForStatuses, 6, rowForStatuses, 8, mapStatusDesc[st], data_format)
            worksheet.write_number(rowForStatuses, 9, num, data_format)
            rowForStatuses += 1

        workbook.close()


class ABPM(Report):

    def __init__(self, month: int, year: int):
        super().__init__(month=month, year=year)
        self.mapWorkersAndInit()

    def mapWorkersAndInit(self):
        for i in range(len(statuses)):
            self.statusMap[statuses[i]] = str(i)
            self.statusNumOfPatients[str(i)] = 0

    def addPatient(self, dt: date, name: str, surname: str, status: str, doctor: str | None, nurse: str | None):
        mappedStatus: int = self.statusMap[status]
        self.patients.append(Patient(dt=dt,
                                     name=name,
                                     surname=surname,
                                     status=mappedStatus,
                                     doctor=None,
                                     nurse=None))
        self.statusNumOfPatients[mappedStatus] = self.statusNumOfPatients[mappedStatus] + 1

    def removePatientByIndex(self, index: int):
        patient: Patient = self.patients.pop(index)
        self.statusNumOfPatients[patient.status] = self.statusNumOfPatients[patient.status] - 1

    def save(self, filePath: str):
        file = open(filePath, 'w')
        serializablePatients = [p.toDict() for p in self.patients]
        jsonSave = {
            'month': self.month,
            'year': self.year,
            'statusesMap': self.statusMap,
            'statusNumOfPatients': self.statusNumOfPatients,
            'patients': serializablePatients
        }
        json.dump(jsonSave, file)
        file.close()

    def load(self, filePath: str):
        file = open(filePath, 'r')
        jsonLoad = json.load(file)
        file.close()
        self.month = jsonLoad['month']
        self.year = jsonLoad['year']
        self.statusMap = jsonLoad['statusesMap']
        self.statusNumOfPatients = jsonLoad['statusNumOfPatients']
        self.patients = []
        for p in jsonLoad['patients']:
            self.patients.append(Patient(dt=datetime.strptime(p['date'], '%d/%m/%Y').date(),
                                         name=p['name'],
                                         surname=p['surname'],
                                         status=p['status'],
                                         doctor=None,
                                         nurse=None))

    def exportToXLSX(self, filePath: str):
        workbook = xlsxwriter.Workbook(filePath)
        worksheet = workbook.add_worksheet(mapMonth(self.month).upper())
        header_format1 = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'vcenter',
            'center_across': 'true',
            'bold': 'true',
            'font_size': 11,
            'text_wrap': 'true'
        })

        header_format2 = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'vcenter',
            'center_across': 'true',
            'bold': 'true',
            'font_size': 14,
        })

        data_format = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'vcenter',
            'center_across': 'true',
            'font_size': 11
        })

        date_format = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'vcenter',
            'center_across': 'true',
            'font_size': 11,
            'num_format': 'd.m.yyyy'
        })

        worksheet.merge_range(0, 0, 2, 4,
                              'ODSEK ZA ENDOKRINOLOGIJU KARDIOVASKULARNOG SISTEMA\nI OSTEODENZITOMETRIJU',
                              header_format1)
        worksheet.merge_range(3, 0, 4, 4,
                              f'MESEČNI IZVEŠTAJ ZA {mapMonth(self.month).upper()} {self.year} ABPM',
                              header_format2)

        worksheet.merge_range(5, 0, 6, 0, 'Datum', header_format1)
        worksheet.merge_range(5, 1, 6, 3, 'Prezime i ime pacijenta', header_format1)
        worksheet.merge_range(5, 4, 6, 4, 'Odeljenje', header_format1)

        currentRow = 7

        reverseMapStatus = reverseDict(self.statusMap)

        for patient in self.patients:
            worksheet.write_datetime(currentRow, 0, patient.dt, date_format)
            worksheet.merge_range(currentRow, 1, currentRow, 3, f'{patient.surname} {patient.name}', data_format)
            worksheet.write_string(currentRow, 4, reverseMapStatus[patient.status], data_format)
            currentRow += 1

        s = {}

        statusSumNumPatients = 0

        for stat, num in self.statusNumOfPatients.items():
            if num != 0:
                s[reverseMapStatus[stat]] = num
                statusSumNumPatients += num

        if (len(s) + 3) < 60 - currentRow % 60:
            currentRow += 2
        else:
            currentRow += 60 - currentRow % 60

        worksheet.write_string(currentRow, 0, 'ABPM', header_format1)
        worksheet.write_number(currentRow, 1, statusSumNumPatients, header_format1)

        currentRow += 1

        for st, num in s.items():
            worksheet.write_string(currentRow, 0, st, data_format)
            worksheet.write_number(currentRow, 1, num, data_format)
            currentRow += 1

        workbook.close()


class ReportManager:
    def __init__(self):
        importData()
        self.reports = {}

    def create(self, month: int, year: int, reportType: int) -> None | str:
        try:
            if reportType == 0:
                self.reports[(month, year, reportType)] = DXA(month=month, year=year)
            else:
                self.reports[(month, year, reportType)] = ABPM(month=month, year=year)
            return None
        except:
            return traceback.format_exc()

    def delete(self, month: int, year: int, reportType: int) -> None | str:
        try:
            del self.reports[(month, year, reportType)]
            return None
        except:
            return traceback.format_exc()

    def save(self, month: int, year: int, reportType: int, filePath: str) -> None | str:
        try:
            self.reports[(month, year, reportType)].save(filePath)
            return None
        except:
            return traceback.format_exc()

    def load(self, filePath: str) -> None | DXA | ABPM | str:
        try:
            extension = filePath.split('.')[1].lower()
            if extension == 'dxa':
                dxa = DXA(0, 0)
                dxa.load(filePath)
                self.reports[(dxa.month, dxa.year, 0)] = dxa
                return dxa
            elif extension == 'abpm':
                abpm = ABPM(0, 0)
                abpm.load(filePath)
                self.reports[(abpm.month, abpm.year, 1)] = abpm
                return abpm
            else:
                # todo FileNotSupported
                pass
            return None
        except:
            return traceback.format_exc()

    def exportToXLSX(self, month: int, year: int, reportType: int, filePath: str) -> None | str:
        try:
            self.reports[(month, year, reportType)].exportToXLSX(filePath)
            return None
        except:
            return traceback.format_exc()

    def getReport(self, month: int, year: int, reportType: int) -> Report:
        return self.reports[(month, year, reportType)]


'''if __name__ == "__main__":
    importData()
    manager: ReportManager = ReportManager()
    manager.create(4, 2024, 0)
    manager.create(4, 2024, 1)
    dxa = manager.getReport(4, 2024, 0)
    abpm = manager.getReport(4, 2024, 1)
    dxa.addPatient(dt=date.today(), name='Marko', surname='Gloginja', status='DB', doctor='Pavlovic Natalija',
                   nurse='Simjanovic Sandra')
    dxa.addPatient(dt=date.today(), name='Katarina', surname='Gloginja', status='L', doctor='Pavlovic Natalija',
                   nurse='Simjanovic Sandra')
    dxa.addPatient(dt=date.today(), name='Nikola', surname='Velickovic', status='G', doctor='Pavlovic Natalija',
                   nurse='Simjanovic Sandra')
    abpm.addPatient(dt=date.today(), name='Marko', surname='Gloginja', status='C1', doctor=None, nurse=None)
    abpm.addPatient(dt=date.today(), name='Katarina', surname='Gloginja', status='C4', doctor=None, nurse=None)
    abpm.addPatient(dt=date.today(), name='Nikola', surname='Velickovic', status='A', doctor=None, nurse=None)
    dxa.load('dxa.json')
    dxa.exportToXLSX('dxa.xlsx')
    # dxa.removePatientByIndex(1)
    abpm.load('abpm.json')
    abpm.exportToXLSX('abpm.xlsx')'''
