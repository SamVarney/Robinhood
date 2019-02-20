#from Robinhood import endpoints
from Robinhood import Robinhood
import time
import config

#Setup
my_trader = Robinhood()
#login
my_trader.login(username=config.USERNAME, password=config.PASSWORD)


#my_trader.print_quotes(stocks=["BBRY", "FB", "MSFT"])

#Get stock information
    #Note: Sometimes more than one instrument may be returned for a given stock symbol
stock_instrument = my_trader.instruments("GEVO")[0]
print stock_instrument
#Get a stock's quote
#my_trader.print_quote('AAPL')

#Prompt for a symbol
#my_trader.print_quote()

#Print multiple symbols
#my_trader.print_quotes(stocks=["BBRY", "FB", "MSFT"])

#View all data for a given stock ie. Ask price and size, bid price and size, previous close, adjusted previous close, etc.
quote_info = my_trader.quote_data("GEVO")
print(quote_info)

#Place a buy order (uses market bid price)
#buy_order = my_trader.place_buy_order(stock_instrument, 1)

#Place a sell order
#sell_order = my_trader.place_sell_order(stock_instrument, 1)

portfolio = my_trader.portfolios()
positions = my_trader.positions()
securities = my_trader.securities_owned()

while True:
    for key in securities['results']:

        instrument = my_trader.get_url(key['instrument']) #get symbol of stock
        name = instrument['symbol']

        # no get out position info
        quantity_owned = float(key['quantity'])
        price_bought = float(key['pending_average_buy_price'])
        quote = my_trader.quote_data(name)
        print quote
        last_price = float(quote['last_trade_price'])
        time_of_last_price = quote['updated_at']

        # write to the file
        with open('price_{}.csv'.format(name), 'a') as fd:
            line = str(time_of_last_price) + ', ' + str(last_price) + '\n'
            fd.write(line)

        print"-------"
        print name + ':'
        print ('Info  : ' + str(quantity_owned) + ' shares bought for $' + str(price_bought) + ' per share. Now at $' + str(last_price))
        print ('Return: $' + str(quantity_owned*(last_price-price_bought)))
        #print key

    time.sleep(30)

#my_trader.place_market_sell_order(symbol='EXTR', quantity=1, time_in_force='GTC')


print("******************")