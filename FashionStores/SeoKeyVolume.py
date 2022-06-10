import json
import os
import openpyxl
import requests
import xlsxwriter
from py_linq import Enumerable

domainAndUrl = 'https://bfcb-154-6-25-129.ngrok.io/api/'


def ParseCSVFiles():
    print('Reading & Parsing CSV Files')

    mainFolder = os.path.join(str((os.path.dirname(os.path.abspath(__file__)))), "SeoData")
    for gender in os.listdir(mainFolder):
        genderFolder = os.path.join(mainFolder, gender)

        for filterType in os.listdir(genderFolder):
            if os.path.exists(os.path.join(genderFolder, filterType)):
                if '~$' in filterType:
                    continue

                folderPath = os.path.join(
                    os.path.join(str((os.path.dirname(os.path.abspath(__file__)))), "SeoKeywords"),
                    gender.title() + filterType.title().replace('_', "") + '.xlsx')
                wb = xlsxwriter.Workbook(folderPath)
                ws = wb.add_worksheet(filterType.title())

                typeFolder = os.path.join(genderFolder, filterType)

                col1 = 0
                col2 = 1

                for filterName in os.listdir(typeFolder):
                    if os.path.exists(os.path.join(typeFolder, filterName)) and '.xlsx' in filterName:
                        nameFolder = os.path.join(typeFolder, filterName)
                        if '~$' in nameFolder:
                            continue

                        print("Name: ", nameFolder)

                        wb_obj = openpyxl.load_workbook(nameFolder).active
                        text = wb_obj['A']
                        if text[1].value is None and text[2].value is None:
                            text = wb_obj['B']
                            volume = wb_obj['C']
                        else:
                            volume = wb_obj['B']

                        name = filterName.replace('.xlsx', '').title().replace('Dresses', '').replace('Dress',
                                                                                                      '').strip()
                        ws.write(0, col1, name)
                        ws.write(0, col2, name + " " + 'Volume')

                        count = 1
                        skipWords = ['accessories', 'boot', 'jewelry', 'pant', 'shirt', 'shoes', 'sock', 'shop']
                        for x in range(len(text)):
                            colValue = text[x].value
                            if colValue is None or colValue == 'KeywordHistorical' or type(colValue) == int:
                                continue

                            skipMatch = Enumerable(skipWords).where(
                                lambda x: str(x).lower() in str(colValue).lower()).first_or_default()

                            if skipMatch:
                                continue

                            if count > 20:
                                break

                            ws.write(count, col1, colValue)
                            ws.write(count, col2, volume[x].value)
                            count += 1

                        col1 = col1 + 2
                        col2 = col2 + 2

                wb.close()

    print('Parsed Files Successfully\nCreated New CSV Files Successfully')


def GetAuthorizationToken():
    print('GETTING NEW AUTH TOKEN ....!')
    requestHeader = {'Content-Type': 'application/json'}
    postData = '{"email":"leoking627@gmail.com","password":"123456"}'
    loginUrl = domainAndUrl + 'api_auth'
    apiResponse = requests.post(url=loginUrl, data=postData, headers=requestHeader, timeout=6000)
    apiJson = json.loads(apiResponse.content)
    return apiJson['data']['data']["access"]


if __name__ == '__main__':
    accessToken = GetAuthorizationToken()
    print(accessToken)
    requestHeader = {'Content-Type': 'application/json', 'Authorization': accessToken}
    storesDict = requests.get(domainAndUrl + 'top_stores', headers=requestHeader)

    # ParseCSVFiles()
