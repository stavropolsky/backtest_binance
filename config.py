# При написании скрипта использовался python v.3.9. и следующие библиотеки:
# backtraider v1.9.76.123, pandas v.1.5.3, selenium v.4.8.0, beautifulsoup4 v.4.11.2, lxml v.4.9.2, requests v.2.28.2

# Указываем ссылку на страницу с архивами
url = 'https://data.binance.vision/?prefix=data/spot/daily/klines/BTCBUSD/1s/'

# Указываем тикер
symbol = 'BTCBUSD'

# Указываем интервал
interval = '1s'

# Указываем параметры для ордеров
price_buy = 21800
price_sell = 21450
stop_buy_price = 21600
stop_sell_price = 21590
quantity = 0.001


# Указываем период времени для формирования исторических данных, при указании слишком большого временного диапазона,
# потребуется длительное время для формирования данных. После первого запуска скрипта в корневой директории
# формируется файл с данными, в имени которого присутствует временной период и интервал.
# При изменении временного периода и/или интервала и повторного запуска скрипта, файл с данными формируется повторно.
# Если временной период при повторном запуске скрипта не изменяется, повторное формирование файла
# не происходит, что в положительную сторону влияет на скорость работы скрипта, так как данные не нужно
# формировать заново.

start_date = "2023-02-11"
end_date = "2023-02-13"
