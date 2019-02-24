from Robinhood import Robinhood
import config
from structures import Portfolio
from Robinhood.crypto import RobinhoodCrypto
import pandas as pd
import Robinhood.endpoints as end_points
import requests


#Setup
my_trader = Robinhood()

#login
my_trader.login(username=config.USERNAME, password=config.PASSWORD)
#instrument = dict(my_trader.instruments('AGEN')[0])

#agen = Stock(my_trader, instrument)

#Orders
#quote = my_trader.quote_data('AGEN')
#print quote.keys()
#print quote['last_trade_price']
#instrument = dict(my_trader.instruments('AGEN')[0])

#print instrument.keys()
#last_price = float(quote['last_trade_price'])
#time_of_last_price = quote['updated_at']

#my_trader.place_market_sell_order(symbol='AGEN', quantity=1, time_in_force='GTC')

#print quote.keys()
#print my_trader.place_buy_order(instrument=instrument, quantity=1 ,bid_price= last_price)
#raw_input("Are you sure you want to proceed to trade?: ")
#print my_trader.place_market_buy_order(symbol='AGEN', quantity=1, time_in_force='GTC')
#my_trader.place_market_buy_order()

securities = Portfolio(my_trader)

for stock in securities.stocks:
    #print stock.fudamentals
    print stock.url

    try:
        print my_trader.instrument(id = RobinhoodCrypto.PAIRS['BTCUSD'])

    except:
        print 'did not work'

    print RobinhoodCrypto.PAIRS['BTCUSD']
    print stock.id
    print stock.url

for pair in RobinhoodCrypto.PAIRS:
    quote = dict(my_trader.crypto_quote_data(pair = pair))
    print quote['symbol'] + ": " + str(quote)

#print my_trader.get_url(quote_endpoint + str("EXTR"))



#holdings_pd = pd.DataFrame(holdings, columns=holdings.keys())
#print holdings_pd

holdings = my_trader.crypto_holdings()
print holdings

for holding in holdings:
    print "***********************************************************************************"
    print "***********************************************************************************"
    for item in holding:
        print "---------------------------------"
        print item
        print holding[item]

print holdings.keys()
