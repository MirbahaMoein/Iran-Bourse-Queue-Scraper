import os
import sqlite3
import selenium
from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import concurrent.futures
from tkinter import *
from functools import partial
import threading


def get_table(driver):
    element = {}
    element['buy'] = {}
    element['sell'] = {}
    for i in range(5):
        element['buy'][i] = {}
        element['sell'][i] = {}
        try:
            element['buy'][i]['num'] = int(driver.find_element(
                By.XPATH,   value='/html/body/div[4]/form/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[1]'.format(str(i + 2))).text.replace(',', '').replace(' ', '0'))
            element['buy'][i]['volume'] = int(driver.find_element(
                By.XPATH, value='/html/body/div[4]/form/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[2]'.format(str(i + 2))).text.replace(',', '').replace(' ', '0'))
            element['buy'][i]['price'] = int(driver.find_element(
                By.XPATH,  value='/html/body/div[4]/form/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[3]'.format(str(i + 2))).text.replace(',', '').replace(' ', '0'))
            element['sell'][i]['num'] = int(driver.find_element(
                By.XPATH,   value='/html/body/div[4]/form/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[6]'.format(str(i + 2))).text.replace(',', '').replace(' ', '0'))
            element['sell'][i]['volume'] = int(driver.find_element(
                By.XPATH, value='/html/body/div[4]/form/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[5]'.format(str(i + 2))).text.replace(',', '').replace(' ', '0'))
            element['sell'][i]['price'] = int(driver.find_element(
                By.XPATH,  value='/html/body/div[4]/form/div[3]/div[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[4]'.format(str(i + 2))).text.replace(',', '').replace(' ', '0'))
        except:
            pass

    return element


def start_drivers(urls: dict):
    start_drivers.drivers = {}
    start_drivers.tables = {}

    for symbol in urls:
        if urls[symbol] != None:
            start_drivers.drivers[symbol] = webdriver.Chrome(chrome)
            start_drivers.drivers[symbol].get(urls[symbol])
    time.sleep(5)


def update_tables():
    tables = {}
    for symbol in main_menu.urls:
        if main_menu.urls[symbol] != None:
            tables[symbol] = get_table(start_drivers.drivers[symbol])
        else:
            tables[symbol] = None
    for symbol in main_menu.urls:
        try:
            threading.Thread(
                target=start_drivers.drivers[symbol].refresh).start()
        except:
            pass

    start_drivers.tables = tables
    queue()

    update_tables.keep_updating = main_menu.gui.after(5000, update_tables)


def get_url(symbol: str):
    get_urls.driver.find_element(By.ID, value='SearchKey').clear()
    symbol = symbol.replace('ی', 'ي')
    get_urls.driver.find_element(By.ID, value='SearchKey').send_keys(symbol)
    get_urls.driver.find_element(
        By.ID, value='SearchKey').send_keys(Keys.SPACE)
    get_urls.driver.find_element(
        By.ID, value='SearchKey').send_keys(Keys.BACKSPACE)
    time.sleep(5)
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    for i in range(3):

        try:
            result = get_urls.driver.find_element(
                By.CSS_SELECTOR, value='#SearchResult > div > div.content > table > tbody > tr:nth-child({}) > td:nth-child(1) > a'.format(str(i + 1)))
        except:
            result = None
        try:
            get_urls.driver.find_element(
                By.CSS_SELECTOR, value='#SearchResult > div > div.content > table > tbody > tr:nth-child({}) > td:nth-child(1) > a > span'.format(str(i + 1)))
        except:
            if result != None:
                if result.text[:len(symbol)] == symbol:

                    try:
                        cursor.execute("CREATE TABLE urls (symbol, url)")
                    except:
                        pass
                    url = result.get_attribute('href')
                    cursor.execute(
                        "INSERT INTO urls (symbol, url) VALUES (?, ?)", (symbol, url))
                    connection.commit()
                    connection.close()
                    return url
    connection.close()
    return None


def get_urls(symbols: dict):
    urls = {}
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    needtosearch = False
    for i in range(1, len(symbols) + 1):
        symbols[i] = symbols[i].replace('ی', 'ي')
    for index in symbols:
        try:
            selection = cursor.execute(
                "SELECT url FROM urls WHERE symbol = ?", (symbols[index],)).fetchall()
            if selection[0][0] != None:
                urls[symbols[index]] = selection[0][0]
            else:
                urls[symbols[index]] = False
                needtosearch = True
        except:
            urls[symbols[index]] = False
            needtosearch = True
    connection.close()
    if needtosearch:
        get_urls.driver = webdriver.Chrome(chrome)
        get_urls.driver.get('http://www.tsetmc.com/Loader.aspx?ParTree=15')
        time.sleep(5)
        get_urls.driver.find_element(
            By.XPATH, value='/html/body/div[3]/div[2]/a[5]').click()
        time.sleep(5)
        for index in symbols:
            if urls[symbols[index]] == False:
                urls[symbols[index]] = get_url(symbols[index])
        get_urls.driver.quit()
    return urls


def main_menu():
    main_menu.side = {}
    main_menu.pricefield = {}
    main_menu.symbolfield = {}
    main_menu.queuevolume = {}
    main_menu.numberofsymbols = 0

    buybtns = {}
    sellbtns = {}
    queuelabels = {}

    def add_symbol():
        removebtn['state'] = 'normal'

        main_menu.numberofsymbols += 1

        sidevar = StringVar(main_menu.gui, 'buy')
        main_menu.side[main_menu.numberofsymbols] = sidevar
        buybtn = Radiobutton(
            main_menu.gui, variable=main_menu.side[main_menu.numberofsymbols], value='buy')
        sellbtn = Radiobutton(
            main_menu.gui, variable=main_menu.side[main_menu.numberofsymbols], value='sell')
        buybtns[main_menu.numberofsymbols] = buybtn
        sellbtns[main_menu.numberofsymbols] = sellbtn
        sellbtn.grid(row=main_menu.numberofsymbols, column=1)
        buybtn.grid(row=main_menu.numberofsymbols, column=2)

        pricefield = Text(main_menu.gui, width=6, height=1)
        main_menu.pricefield[main_menu.numberofsymbols] = pricefield
        pricefield.grid(row=main_menu.numberofsymbols, column=3)

        symbolfield = Text(main_menu.gui, width=8, height=1)
        main_menu.symbolfield[main_menu.numberofsymbols] = symbolfield
        symbolfield.grid(row=main_menu.numberofsymbols, column=4)

        addbtn.grid(row=main_menu.numberofsymbols + 1, column=4)
        removebtn.grid(row=main_menu.numberofsymbols + 1, column=3)
        startbtn.grid(row=main_menu.numberofsymbols + 1, column=0)
        queuevolume = IntVar(main_menu.gui, 0)
        queuelabel = Label(main_menu.gui, textvariable=queuevolume)
        queuelabels[main_menu.numberofsymbols] = queuelabel
        queuelabel.grid(row=main_menu.numberofsymbols, column=0)
        main_menu.queuevolume[main_menu.numberofsymbols] = queuevolume

    def remove_symbol():
        main_menu.pricefield[main_menu.numberofsymbols].destroy()
        main_menu.symbolfield[main_menu.numberofsymbols].destroy()
        buybtns[main_menu.numberofsymbols].destroy()
        sellbtns[main_menu.numberofsymbols].destroy()
        queuelabels[main_menu.numberofsymbols].destroy()
        startbtn.grid_forget()
        addbtn.grid_forget()
        removebtn.grid_forget()

        main_menu.numberofsymbols -= 1
        if main_menu.numberofsymbols == 0:
            removebtn['state'] = 'disabled'
        addbtn.grid(row=main_menu.numberofsymbols + 1, column=4)
        removebtn.grid(row=main_menu.numberofsymbols + 1, column=3)
        startbtn.grid(row=main_menu.numberofsymbols + 1, column=0)

    def start_updating():
        startbtn['text'] = 'اعمال تغییرات'

        main_menu.symbols = {}
        main_menu.prices = {}
        main_menu.sides = {}
        for i in range(1, main_menu.numberofsymbols + 1):
            main_menu.symbols[i] = main_menu.symbolfield[i].get(
                '1.0', 'end-1c')
            main_menu.prices[i] = int(
                main_menu.pricefield[i].get('1.0', 'end-1c'))
            main_menu.sides[i] = main_menu.side[i].get()
        main_menu.urls = get_urls(main_menu.symbols)
        start_drivers(main_menu.urls)
        main_menu.thread = threading.Thread(target=update_tables)
        main_menu.thread.start()

    def manage_threads_start():
        try:
            main_menu.gui.after_cancel(update_tables.keep_updating)
        except:
            pass
        updatethread = threading.Thread(target=start_updating)
        updatethread.start()

    main_menu.gui = Tk('mainMenu')
    main_menu.gui.title('منو')
    Label(main_menu.gui, text='حجم صف').grid(row=0, column=0)
    Label(main_menu.gui, text='فروش').grid(row=0, column=1)
    Label(main_menu.gui, text='خرید').grid(row=0, column=2)
    Label(main_menu.gui, text='قیمت').grid(row=0, column=3)
    Label(main_menu.gui, text='نماد').grid(row=0, column=4)

    addbtn = Button(main_menu.gui, text='اضافه کردن', command=add_symbol)
    addbtn.grid(row=main_menu.numberofsymbols + 1, column=4)
    removebtn = Button(main_menu.gui, text='حذف کردن', command=remove_symbol)
    removebtn.grid(row=main_menu.numberofsymbols + 1, column=3)
    removebtn['state'] = 'disabled'

    startbtn = Button(main_menu.gui, text='شروع', command=manage_threads_start)
    startbtn.grid(row=main_menu.numberofsymbols + 1, column=0)

    main_menu.gui.mainloop()

    try:
        for symbol in start_drivers.drivers:
            start_drivers.drivers[symbol].quit()
    except:
        pass


def queue():
    volumeinqueue = {}
    for i in range(1, len(main_menu.symbols) + 1):
        symbol = main_menu.symbols[i]
        side = main_menu.sides[i]
        price = main_menu.prices[i]
        volumeinqueue[i] = 0
        if start_drivers.tables[symbol] != None:
            for j in start_drivers.tables[symbol][side]:
                askbidvolume = start_drivers.tables[symbol][side][j]['volume']
                askbidprice = start_drivers.tables[symbol][side][j]['price']
                if side == 'buy':
                    if askbidprice >= price:
                        volumeinqueue[i] += askbidvolume
                elif side == 'sell':
                    if askbidprice <= price:
                        volumeinqueue[i] += askbidvolume
        main_menu.queuevolume[i].set(volumeinqueue[i])


chrome = ChromeDriverManager()
chrome = chrome.install()

main_menu()
