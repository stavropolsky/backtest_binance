# Specify a link to the page with archives, for example: url = 'https://data.binance.vision/?prefix=data/spot/daily/klines/BTCBUSD/1s/'
url = ''

# Specify the ticker, for example: symbol = 'BTCBUSD'
symbol = ''

# Specify the interval, for example: interval = '1s'
interval = ''

# Specify parameters for orders, for example:
# price_buy = 21800
# price_sell = 21450
# stop_buy_price = 21600
# stop_sell_price = 21590
# quantity = 0.001

price_buy =
price_sell =
stop_buy_price =
stop_sell_price =
quantity =


# Specify the period of time for the formation of historical data, if the time range is too large,
# it will take a long time to generate the data. After the first run of the script in the root directory
# a data file is formed, the name of which contains a time period and an interval.
# When changing the time period and/or interval and restarting the script, the data file is regenerated.
# If the time period does not change when the script is restarted, the file is regenerated
# does not happen, which in a positive way affects the speed of the script, since the data is not needed
# rebuild, for example:
# start_date = "2023-02-11"
# end_date = "2023-02-13"
start_date = ""
end_date = ""
