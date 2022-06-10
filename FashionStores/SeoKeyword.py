import os
import csv
import openpyxl
from py_linq import Enumerable


def ParseCSVFiles():
    filterList = []
    categoryList = []

    print('Reading & Parsing CSV Files')

    mainFolder = os.path.join(str((os.path.dirname(os.path.abspath(__file__)))), "SeoData")
    for gender in os.listdir(mainFolder):
        genderFolder = os.path.join(mainFolder, gender)

        for filterType in os.listdir(genderFolder):
            if os.path.exists(os.path.join(genderFolder, filterType)):
                if '~$' in filterType:
                    continue

                parentCategory = gender
                if filterType == 'garment_care' or filterType == 'season':
                    parentCategory = ''

                typeFolder = os.path.join(genderFolder, filterType)

                for filterName in os.listdir(typeFolder):
                    if os.path.exists(os.path.join(typeFolder, filterName)) and '.xlsx' in filterName:
                        nameFolder = os.path.join(typeFolder, filterName)
                        if '~$' in nameFolder:
                            continue

                        print("Name: ", nameFolder)

                        seoKeyList = []
                        wb_obj = openpyxl.load_workbook(nameFolder).active
                        text = wb_obj['A']
                        if text[1].value is None and text[2].value is None:
                            text = wb_obj['B']

                        skipWords = ['accessories', 'boot', 'jewelry', 'pant', 'shirt', 'shoes', 'sock', 'shop']
                        for x in range(len(text)):
                            colValue = text[x].value
                            if colValue is None or colValue == 'KeywordHistorical' or type(colValue) == int:
                                continue

                            skipMatch = Enumerable(skipWords).where(
                                lambda x: str(x).lower() in str(colValue).lower()).first_or_default()

                            if skipMatch:
                                continue

                            seoKeyList.append(colValue)

                        seoKeywords = ",".join(list(seoKeyList))

                        if filterType == 'category':
                            categoryList.append([parentCategory, filterName.replace(".xlsx", "").title(), seoKeywords])
                        else:
                            filterList.append([parentCategory, filterType.replace(".xlsx", ""),
                                               str(filterName.replace(".xlsx", "").replace('3BY4',
                                                                                           '3/4').title().replace(
                                                   ' Dresses', '').replace(' Dress', '')).strip(), seoKeywords])

    print('Parsed Files Successfully')

    with open('CategoryKeyword.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        catHeader = ['parent_category_name', 'category_type', 'seo_keywords']
        writer.writerow(catHeader)
        writer.writerows(categoryList)

    with open('FilterKeyword.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        filHeader = ['parent_category_name', 'filter_type', 'filter_name', 'seo_keywords']
        writer.writerow(filHeader)
        writer.writerows(filterList)

    print('Created New CSV Files Successfully')


if __name__ == '__main__':
    ParseCSVFiles()