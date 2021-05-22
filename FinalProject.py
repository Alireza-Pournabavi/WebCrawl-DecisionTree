# Final Project
# timecheh Super Market Search & Prediction Price

# import
import requests
import re
from bs4 import BeautifulSoup as bs
import mysql.connector as mysql
import pandas as pd
from sklearn.tree import DecisionTreeRegressor


def webCrawl():
    ID = 1
    ID_detect = 0
    # Open log file
    logFile = open('timchehAPI-log.txt', 'a')
    # Open Main Page
    maxPage, countPage = 1, 1  # for count and find Max Page
    main_url = 'https://timcheh.com/search/category-power-bank?has_selling_stock=1&page={}'  # Main URL

    # Find Page of Products
    while countPage <= maxPage:  # Count & cursor on every Page of Products
        try:
            # Find Max Page
            main_req = requests.get(main_url.format(countPage))
            maxPage_soup = bs(main_req.text, 'html.parser')
            maxPage_regex = maxPage_soup.find_all(
                "div", attrs={"class": "styles_custom_pagination__L0O9q"})
            maxPage_array = re.findall(r"button\"\>(\d+)<", str(maxPage_regex))
            if maxPage <= int(maxPage_array[-1]):
                maxPage = int(maxPage_array[-1])
        except:
            pass

        # log file
        print('page number: ' + str(countPage))
        logFile.writelines('page number: ' + str(countPage) + '\n')
        print(main_url.format(countPage) + '\n')
        logFile.writelines(main_url.format(countPage) + '\n\n')

        # Extract Product in Page
        try:
            main_soup = bs(main_req.text, 'html.parser')
            main_regex = main_soup.find_all('li', attrs={'class': 'category_styles_product_card_item__6xFp-'})
            main_regex = str(main_regex).split('<li')
        except:
            countPage += 1
            continue

        # Find Product Page
        for product in main_regex:  # Any of Products in Page
            try:
                # Extract Link of Product
                reg = re.findall(r'class.*href=\"(.*?)\"', product)
                if not reg:  # Null Output of above line
                    continue

                # Specifications
                # Extract Information
                # requests & bs4 for any Products
                product_req = requests.get('https://timcheh.com' + reg[0])
                product_soup = bs(product_req.text, 'html.parser')

                # Product ID
                product_ID = re.findall(r'tpi\-(\d+)', reg[0])

                # log file
                print('product: ' + str(ID))
                logFile.writelines('product: ' + str(ID) + '\n')
                print('product id: ' + str(product_ID[0]))
                logFile.writelines('product id: ' + str(product_ID[0]) + '\n')
                print('link: ' + 'https://timcheh.com' + reg[0])
                logFile.writelines('link: ' + 'https://timcheh.com' + reg[0] + '\n')

                # Name Product
                product_name = re.findall(r'\<h1.*\>(.+?)\<', str(product_soup.find("h1")))
                product_name = product_name[0]
                # Prise Product
                product_price = product_soup.find("span", attrs={"class": "product_styles_price__3Ws3t"})
                product_price = re.findall(r'\<span.*\>(.+?)\<', str(product_price))
                product_price = product_price[0]
                product_price = product_price.split(',')
                product_price = product_price[0] + product_price[1]
                # Weight Product //regex
                product_weight = re.findall(r'\\u003eوزن\\u003c.*class\=\\\"value\\\"\\u003e(\d+?)\W*\sگرم\\u003c',
                                            str(product_soup))
                product_weight = product_weight[0]
                # Capacity & Number of Output Product //bs4 //regex
                info_soup = product_soup.find_all("li", attrs={"class": "product_styles_item__JnLL-"})  # ظرفیت، درگاه،
                info_regex = re.findall(r".*ظرفیت اسمی \: (\d+?)\s.*تعداد درگاه خروجی \:\s(\d+)\s", str(info_soup))
                product_capacity = info_regex[0][0]
                product_output = info_regex[0][1]

                # log file
                print('prise: ' + product_price)
                logFile.writelines('prise: ' + product_price + '\n')
                print('weight: ' + product_weight)
                logFile.writelines('weight: ' + product_weight + '\n')
                print('capacity: ' + product_capacity)
                logFile.writelines('capacity: ' + product_capacity + '\n')
                print('output: ' + product_output + '\n\n')
                logFile.writelines('output: ' + product_output + '\n\n\n')

                # Insert Data into Database
                cursor.execute(
                    'INSERT INTO timchehAPI.information VALUES (\'%i\', \'%i\', \'%s\', \'%i\',\'%i\',\'%i\',\'%i\')' % (
                        int(ID), int(product_ID[0]), product_name, int(product_weight), int(product_capacity),
                        int(product_output), int(product_price)))
                db.commit()

                # Update ID
                ID += 1
                ID_detect += 1
            except:
                ID += 1
                print()
                logFile.writelines('\n')
                continue

        # Update countPage
        countPage += 1

    # Accuracy
    # log File
    productNumber_req = requests.get(main_url.format(1))
    productNumber_soup = bs(productNumber_req.text, 'html.parser')
    productNumber_regex = productNumber_soup.find_all(
        "div", attrs={"class": "category_styles_count_pro_abs__29fX-"})
    productNumber_array = re.findall(r">(\d+?)<", str(productNumber_regex))

    cal1 = ID - 1
    cal2 = ((ID - 1) * 100) / int(productNumber_array[0])
    cal3 = (ID_detect * 100) / int(productNumber_array[0])
    print('Accuracy of This Web Scraping:\n')
    print('Actual number of Products: ', productNumber_array[0])
    print('Number of products detected: ', cal1)
    print('Accuracy: ', cal2)
    print('Number of products identified with complete information: ', ID_detect)
    print('Accuracy: ', cal3, '\n')
    logFile.writelines('Accuracy of This Web Scraping:\n')
    logFile.writelines('Actual number of Products: ' + productNumber_array[0] + '\n')
    logFile.writelines('Number of products detected: ' + str(cal1) + '\n')
    logFile.writelines('Accuracy: ' + str(cal2) + '\n')
    logFile.writelines('Number of products identified with complete information: ' + str(ID_detect) + '\n')
    logFile.writelines('Accuracy: ' + str(cal3) + '\n\n')

    # close logFile
    logFile.close()


def predictFunction():
    dataFrame = pd.read_csv('timchehAPI.csv')
    x = pd.DataFrame(dataFrame, columns=['3', '4', '5'])
    y = dataFrame['6']
    dtr = DecisionTreeRegressor()
    dtr.fit(x, y)
    return dtr


if __name__ == "__main__":
    # Connect to Database
    db = mysql.connect(
        host='127.0.0.1',
        user='root',
        password='pass'
    )

    cursor = db.cursor()

    cursor.execute('CREATE DATABASE IF NOT EXISTS timchehAPI;')
    cursor.execute("""CREATE TABLE IF NOT EXISTS timchehAPI.information(
        ID INT, 
        Product_ID INT, 
        Name VARCHAR(120) CHARACTER SET utf8, 
        Weight INT, 
        Capacity INT, 
        Number_of_Output_Ports INT, 
        Price INT
        );""")
    db.commit()

    # Call webCrawl Function
    webCrawl()

    cursor.execute("SELECT * FROM timchehAPI.information;")
    records = cursor.fetchall()
    # for index in records:
    # index[2] = sys.stdout.buffer.write(index[2].encode("utf-8"))
    df = pd.DataFrame(records)
    df.to_csv('timchehAPI.csv')

    db.close()

    # Call & run predictFunction
    t = predictFunction()

    bol = True
    while bol:
        if input('if you want predict powerbank price pleane Enter [y|n]? -> ') == 'y':
            w = int(input('Enter Weight Product: '))
            c = int(input('Enter Capacity Product: '))
            o = int(input('Enter Number of Output Product: '))
            answer = t.predict([[w, c, o]])
            print('Predict prise of your Specifications is {}\n'.format(int(answer[0])))
        else:
            bol = False
    else:
        print('Thank you for Run this Program. Good Luck!!!')
