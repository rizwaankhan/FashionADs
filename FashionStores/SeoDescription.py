import os
import csv
import docx


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
                    if os.path.exists(os.path.join(typeFolder, filterName)) and '.docx' in filterName:
                        nameFolder = os.path.join(typeFolder, filterName)
                        if '~$' in nameFolder:
                            continue

                        print("Name: ", nameFolder)

                        description = ''
                        if os.path.exists(nameFolder):
                            fullText = []
                            document = docx.Document(nameFolder)
                            for para in document.paragraphs:
                                fullText.append(para.text)
                            description = ' '.join(fullText)

                        if filterType == 'category':
                            categoryList.append(
                                [parentCategory, filterName.replace(".docx", "").title(), description])
                        else:
                            filterList.append([parentCategory, filterType.replace(".docx", ""),
                                               str(filterName.replace(".docx", "").replace('3BY4',
                                                                                           '3/4').title().replace(
                                                   'Dresses', '').replace('Dress', '')).strip(), description])

    print('Parsed Files Successfully')

    with open('CategoryDescription.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        catHeader = ['parent_category_name', 'category_type', 'description']
        writer.writerow(catHeader)
        writer.writerows(categoryList)

    with open('FilterDescription.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        filHeader = ['parent_category_name', 'filter_type', 'filter_name', 'description']
        writer.writerow(filHeader)
        writer.writerows(filterList)

    print('Created New CSV Files Successfully')


if __name__ == '__main__':
    ParseCSVFiles()
