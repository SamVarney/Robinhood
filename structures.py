

from Robinhood import Robinhood
import config
import pandas as pd
from datetime import time, datetime

#my_trader = Robinhood()


def instrument_info(instrument):
    return instrument['symbol']

class Portfolio:
    def __init__(self, my_trader):
        self.trader = my_trader
        securities = my_trader.securities_owned()['results']

        self.stocks = []
        for item in securities:
            instrument = dict(self.trader.get_url(item['instrument']))
            self.stocks.append(Stock(self.trader, instrument))


        for stock in self.stocks:
            print stock.general_info()



class Stock:
    def __init__(self, my_trader, instrument):
        self.symbol = instrument['symbol']
        self.id = instrument['id']
        self.fudamentals = instrument['fundamentals']
        self.quote = instrument['quote']
        self.url = instrument['url']
        self.type = instrument['type']

        #Store Trader instance (not sure this is Kosher but will do for now)
        #TODO: revist storing a Trader instance in each stock instance
        self.trader = my_trader

        #Now get info on perfomance since bought
        #Get portfolio
        securities = my_trader.securities_owned()['results']
        pd_securities = pd.DataFrame.from_dict(securities)

        #The keys from Robinhood come as unicode so converting them to strings
        pd_securities.columns = pd_securities.columns.astype(str)

        #get_instrument URL for this stock
        stock = pd_securities[pd_securities['instrument'] == instrument['url']]

        #Use instrument to
        self.avg_buy_cost = float(stock['average_buy_price'].values[0])
        self.quantity_owned = float(stock['quantity'].values[0])


    def get_quote(self):
        #use instrument url to get current quote prices
        quote = dict(self.trader.quote_data(self.symbol))

        #Selling Info
        self.bid_price = float(quote['bid_price'])
        self.bid_size = float(quote['bid_size'])

        #Buying Info
        self.ask_price = float(quote['ask_price'])
        self.ask_size = float(quote['ask_size'])

        #Quote Update Time (don't plan to use for a bit)
        self.quote_time = datetime.strptime(str(quote['updated_at']),'%Y-%m-%dT%H:%M:%SZ') #Assuming it will always come as UTC (Z)
        return


    #Methods for summarizing information on stock

    def all_info(self):

        self.general_info()
        self.quote_info()

        return dict({'symbol': self.symbol,
                'quantity': self.quantity_owned,
                'Cost': self.avg_buy_cost})


    def general_info(self):
        self.get_quote() #update for most current price

        print '\n__________General Info for {}___________'.format(self.symbol)
        print 'Symbol: {}'.format(self.symbol)
        print '# Owned: {}'.format(self.quantity_owned)
        print 'Avg Buy Cost: ${}'.format(self.avg_buy_cost)
        print 'Return:       ${}'.format(self.bid_price*self.quantity_owned - self.avg_buy_cost*self.quantity_owned)
        print '----------------------------------\n'


    #Print quote info nicely
    def quote_info(self):
        #update quote
        self.get_quote()

        #print it nicely
        print '\n__________Quote for {}___________'.format(self.symbol)
        print 'Updated: {}'.format(self.quote_time)
        print 'Bid: ${} (Vol: {})'.format(self.bid_price, self.bid_size)
        print 'Ask: ${} (Vol: {})'.format(self.ask_price, self.ask_size)
        print '----------------------------------\n'

        return

#Setup
my_trader = Robinhood()

#login
my_trader.login(username=config.USERNAME, password=config.PASSWORD)
instrument = dict(my_trader.instruments('AGEN')[0])

agen = Stock(my_trader, instrument)
print '------------------------'
#agen.all_info()
#agen.quote_info()

port = Portfolio(my_trader)