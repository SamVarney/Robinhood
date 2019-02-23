from Robinhood import Robinhood
import config
from structures import Stock

#Setup
my_trader = Robinhood()

#login
my_trader.login(username=config.USERNAME, password=config.PASSWORD)
instrument = dict(my_trader.instruments('AGEN')[0])

agen = Stock(my_trader, instrument)

#Orders
quote = my_trader.quote_data('AGEN')
print quote.keys()
print quote['last_trade_price']
instrument = dict(my_trader.instruments('AGEN')[0])

print instrument.keys()
last_price = float(quote['last_trade_price'])
time_of_last_price = quote['updated_at']

#my_trader.place_market_sell_order(symbol='AGEN', quantity=1, time_in_force='GTC')

#print quote.keys()
#print my_trader.place_buy_order(instrument=instrument, quantity=1 ,bid_price= last_price)
#raw_input("Are you sure you want to proceed to trade?: ")
#print my_trader.place_market_buy_order(symbol='AGEN', quantity=1, time_in_force='GTC')
#my_trader.place_market_buy_order()