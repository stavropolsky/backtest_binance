from config import price_buy, price_sell, stop_buy_price, stop_sell_price, quantity, start_date, end_date, url, symbol,\
    interval
import pandas as pd
import backtrader as bt
from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup
import re
import os
import zipfile
import csv
import io
from selenium.webdriver.chrome.options import Options

global df


def get_data(link):
    global all_csv_contents
    options = Options()
    options.set_preference = ('general.useragent.override',
                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                              ' Chrome/110.0.0.0 Safari/537.36')
    options.add_argument('--no-sandbox')
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(
            executable_path='chromedriver',
            options=options
        )
        driver.get(url=link)
        time.sleep(20)

        with open('index.html', 'w', encoding="utf-8") as file:
            file.write(driver.page_source)
        driver.close()
        driver.quit()
    except Exception as ex:
        print(ex)

    with open('index.html', encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')

    # Создание директории для сохранения csv файлов
    if not os.path.exists('csv_files'):
        os.mkdir('csv_files')

    # Создание пустого списка для хранения содержимого csv файлов
    # csv_contents = []

    # Поиск всех ссылок на zip архивы
    zip_links = soup.find_all('a', href=re.compile(f'{symbol}-{interval}-\\d{{4}}-\\d{{2}}-\\d{{2}}\\.zip$'))

    # Цикл по ссылкам на zip архивы
    for zip_link in zip_links:
        # Получение ссылки на zip архив и даты
        zip_url = zip_link['href']
        date_str = re.search('\\d{4}-\\d{2}-\\d{2}', zip_link['href']).group()

        # Проверка, находится ли дата в указанном периоде
        if start_date <= date_str <= end_date:
            # Проверка, что это не ссылка на файл с расширением .CHECKSUM
            if not zip_url.endswith('.CHECKSUM'):
                # Загрузка zip архива
                zip_response = requests.get(zip_url)

                # Распаковка zip архива
                zip_file = zipfile.ZipFile(io.BytesIO(zip_response.content))
                zip_file.extractall('csv_files')
                zip_file.close()

                # Чтение содержимого csv файлов
                all_csv_contents = set()
                for file_name in os.listdir('csv_files'):
                    if file_name.endswith('.csv'):
                        csv_contents = []
                        # Чтение csv файла и удаление ненужных колонок
                        df_ = pd.read_csv(os.path.join('csv_files', file_name), header=None, usecols=[0, 1, 2, 3, 4, 5])
                        # Преобразование даты
                        df_[0] = pd.to_datetime(df_[0], unit='ms')
                        # Преобразование DataFrame в множество строк
                        csv_contents = set(map(tuple, df_.values.tolist()))

                        # Добавление содержимого csv файла в общее множество строк
                        all_csv_contents.update(csv_contents)

            # Сохранение содержимого csv файлов в единый файл
            all_csv_contents = [list(row) for row in sorted(all_csv_contents, key=lambda x: x[0])]
            file = f'historical_data_{start_date}_{end_date}_{interval}.csv'
            with open(file, mode='w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',')
                # Запись заголовков колонок
                csv_writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                for row in all_csv_contents:
                    csv_writer.writerow(row)

    # Удаление содержимого папки csv_files
    for i in os.listdir('csv_files'):
        file_path = os.path.join('csv_files', i)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

    dataframe = pd.read_csv(file, index_col='timestamp', parse_dates=True)
    return dataframe


# Определяем путь к файлу
filename = f'historical_data_{start_date}_{end_date}_{interval}.csv'

# Если файл с данными заданного периода существует, загружаем его в DataFrame
if os.path.exists(filename):
    df = pd.read_csv(filename, index_col='timestamp', parse_dates=True)
# Если файла с данными заданного периода нет, формируем его
else:
    df = get_data(url)


# Переопределяем маркеры
class BuySellArrows(bt.observers.BuySell):
    plotlines = dict(buy=dict(marker='$\u21E7$', markersize=12.0),
                     sell=dict(marker='$\u21E9$', markersize=12.0))


# Определение стратегии
class OrderExecutionStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        # Logging function fot this strategy
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))

    def place_buy_order(self):
        self.buy(price=self.price_buy, exectype=bt.Order.StopLimit, size=self.quantity, pricelimit=self.stop_buy)
        self.counter_orders += 1
        self.log(f'BUY CREATE, Current Price: {self.data[0]}, Price: {self.price_buy}, Stop: {self.stop_buy}')
        print('Размещение лимитного ордера на покупку')

    def place_sell_order(self):
        self.sell(price=self.price_sell, exectype=bt.Order.StopLimit, size=self.quantity, pricelimit=self.stop_sell)
        self.counter_orders += 1
        self.log(f'SELL CREATE, Current Price: {self.data[0]}, Price: {self.price_sell}, Stop: {self.stop_sell}')
        print('Размещение лимитного ордера на продажу')

    def notify_order(self, order):
        if order.status in [order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED', dt=order.created.dt)
            return

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f' % (order.executed.price, order.executed.value))
                self.executed_orders += 1
                self.place_sell_order()
                self.order = True

            if order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f' % (order.executed.price, order.executed.value))
                self.executed_orders += 1
                self.place_buy_order()
                self.order = True

    def __init__(self):
        self.counter_orders = 0
        self.executed_orders = 0
        self.price_buy = price_buy
        self.price_sell = price_sell
        self.stop_buy = stop_buy_price
        self.stop_sell = stop_sell_price
        self.quantity = quantity
        self.order = False
        BuySellArrows(self.data, barplot=True)

    def next(self):
        if not self.order:
            self.place_buy_order()
            self.order = True

    def stop(self):
        print('Количество выставленных ордеров:', self.counter_orders)
        print('Количество исполненных ордеров:', self.executed_orders)


cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)
cerebro.addstrategy(OrderExecutionStrategy)
cerebro.run(stdstats=False)
