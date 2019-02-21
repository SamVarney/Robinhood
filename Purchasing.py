from Robinhood import Robinhood
import config

#Setup
my_trader = Robinhood()

#login
my_trader.login(username=config.USERNAME, password=config.PASSWORD)

#Orders
quote = my_trader.quote_data('AGEN')
print quote.keys()
print quote['last_trade_price']
instrument = dict(my_trader.instruments('AGEN')[0])

print instrument.keys()
last_price = float(quote['last_trade_price'])
time_of_last_price = quote['updated_at']
#print quote.keys()
#print my_trader.place_buy_order(instrument=instrument, quantity=1 ,bid_price= last_price)
print my_trader.place_market_buy_order(symbol='AGEN', quantity=1, time_in_force='GTC')
#my_trader.place_market_buy_order()