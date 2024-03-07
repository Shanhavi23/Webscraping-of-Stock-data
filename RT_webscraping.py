import pandas as pd
import datetime
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import os
import time


def web_content_div(web_content, class_path):
    web_content_div = web_content.find_all('div', {'class': class_path})
    try:
        spans = web_content_div[0].find_all('fin-streamer')
        texts = [span.get_text() for span in spans]
    except IndexError:
        texts = []
    return texts


def content(web_content, class_path):
    web_content_div = web_content.find_all('div', {'class': class_path})
    try:
        spans = web_content_div[0].find_all('td')
        texts = [span.get_text() for span in spans]
    except IndexError:
        texts = []
    return texts


def real_time_price(stock_code):
    url = 'https://finance.yahoo.com/quote/' + stock_code + '?.tsrc=fin-srch'
    try:
        r = requests.get(url)
        web_content = BeautifulSoup(r.text, 'lxml')
        texts = web_content_div(web_content, 'D(ib) Mend(20px)')

        if texts:
            price, change = texts[0], texts[1] + ' ' + texts[2]
        else:
            price, change = [], []
        texts = web_content_div(web_content,
                                'D(ib) W(1/2) Bxz(bb) Pend(12px) Va(t) ie-7_D(i) smartphone_D(b) smartphone_W(100%) smartphone_Pend(0px) smartphone_BdY smartphone_Bdc($seperatorColor)')
        if texts:
            volume = texts[0]
        else:
            volume = []
        texts = content(web_content,
                        'D(ib) W(1/2) Bxz(bb) Pstart(12px) Va(t) ie-7_D(i) ie-7_Pos(a) smartphone_D(b) smartphone_W(100%) smartphone_Pstart(0px) smartphone_BdB smartphone_Bdc($seperatorColor)')
        if texts:
            for count, target in enumerate(texts):
                if target == '1y Target Est':
                    one_year_target = texts[count + 1]
        else:
            one_year_target = []
    except ConnectionError:
        price, change, volume, one_year_target = [], [], [], []
    return price, change, volume, one_year_target


Stock = ['TSLA', 'BRK-B', 'PYPL', 'AAPL', 'AMZN', 'MSFT', 'FB', 'GOOG']
while True:
    d = []
    for stock in Stock:
        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        l = [time_stamp, stock]
        price, change, vol, target = real_time_price(stock)
        l.append(price)
        l.append(change)
        l.append(vol)
        l.append(target)
        d.append(l)

    if not os.path.exists('stock data.csv'):
        df = pd.DataFrame(d, columns=['Timestamp', 'Stock_code', 'Price', 'Changes', 'Volume', 'One_year_target'])
        df.to_csv('stock data.csv', mode='w', index=False)  # Writing to CSV in 'w' mode to overwrite the file
    else:
        df = pd.DataFrame(d, columns=['Timestamp', 'Stock_code', 'Price', 'Changes', 'Volume', 'One_year_target'])
        df.to_csv('stock data.csv', mode='a', index=False, header=False)

    time.sleep(60)  # Sleep for 60 seconds before fetching data again
'''
while (True):
    info = []
    col = []
    time_stamp = datetime.datetime.now() - datetime.timedelta(hours=10,minutes=30)
    time_stamp = time_stamp.strftime('%Y-%m-%d %H:%M:%S')
    for stock_code in Stock:
        stock_price, change, volume, latest_pattern, one_year_target = real_time_price(stock_code)
        info.append(stock_price)
        info.extend([change])
        info.extend([volume])
        info.extend([latest_pattern])
        info.extend([one_year_target])
    col = [time_stamp]
    col.extend(info)
    df = pd.DataFrame(col)
    df = df.T
    df.to_csv(str(time_stamp[0:11]) + 'stock data.csv', mode='a', header=False)
    print(col)
'''
