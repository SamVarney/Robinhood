

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
        print quote
        #Selling Info
        self.bid_price = float(quote['bid_price'])
        self.bid_size = float(quote['bid_size'])

        #Buying Info
        self.ask_price = float(quote['ask_price'])
        self.ask_size = float(quote['ask_size'])

        #Other Info
        self.last_extened_hours_trade_price = quote['last_extended_hours_trade_price'] # for estimating return when markets are closed

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
        if self.bid_price > 0: #TODO: make this acutally work (instead of repeating the same code)
            print 'Return:       ${}'.format(self.bid_price*self.quantity_owned - self.avg_buy_cost*self.quantity_owned) #TODO: should use market price not bid price
        else:
            print 'Return:       ${}'.format(self.bid_price * self.quantity_owned - self.avg_buy_cost * self.quantity_owned)  # TODO: should use market price not bid price
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


class crypto_porfolio:
    def __init__(self, my_trader):
        #Get holdings from robinhood
        holdings = my_trader.crypto_holdings()

        #Create a holding instance for each crypto currency, ignoring the USD currency element that comes at the end
        self.holdings = []
        for holding in holdings:
            cost_bases = holding['cost_bases']  # TODO: will this every return a list with more than 1 element?
            if len(cost_bases) > 0:
                self.holdings.append(cryto_holding(my_trader, holding))

            else: #not a crypto holding
                print "Cost_bases has length of {}".format(len(cost_bases))
                print "Not a holding. Probably the USD item that comes at end of holdings request."


    def general_info(self):
        for holding in self.holdings:
            holding.general_info()

class cryto_holding:
    def __init__(self, my_trader, holding):
        self.trader = my_trader

        #account info
        self.account_id = holding['account_id']
        self.created_at = holding['created_at']
        self.updated_at = holding['updated_at']

        #currency info
        currency = dict(holding['currency'])
        self.code = currency['code']
        self.name = currency['name']
        self.currency_id = currency['id']

        #quantities
        self.quantity_available = float(holding['quantity_available'])
        self.quantity_held_for_sell = float(holding['quantity_held_for_sell'])
        self.quantity_total = float(holding['quantity'])
        self.id = holding['id'] #TODO: Figure out what this id refers to

        #Cost info
        cost_bases = holding['cost_bases'] #TODO: will this every return a list with more than 1 element?
        if len(cost_bases) > 0:
            cost_bases = dict(cost_bases[0])
            self.direct_cost_basis = float(cost_bases['direct_cost_basis'])
            self.direct_quantity = float(cost_bases['direct_quantity'])  # TODO: what is Direct Quantity vs Quantity held?
            self.intraday_cost_basis = float(cost_bases['intraday_cost_basis'])
            if self.quantity_total > 0:
                self.avg_cost_per_coin = self.direct_cost_basis/self.quantity_total #TODO: this lines up w/Value in app but validate the calculation values
            else:
                self.avg_cost_per_coin = None

        else:
            print "cost bases has length of {}".format(len(cost_bases))
            print "Not a holding. Probably the USD item that comes at end of holdings request."


    #quote methods
    def get_quote(self):
        quote = my_trader.crypto_quote_data("{}USD".format(self.code)) #assuming I'll always buy in USD

        #Selling Info
        self.bid_price = float(quote['bid_price'])

        #Buying Info
        self.ask_price = float(quote['ask_price'])

        #TODO: Figure out what each of these mean
        self.high_price = float(quote['high_price'])
        self.low_price = float(quote['low_price'])
        self.volume = float(quote['volume'])
        self.mark_price = float(quote['mark_price'])
        self.open_price = float(quote['open_price'])
        self.quote_id = quote['id'] #TODO: Not sure if this is actually the quote id

        #Quote Update Time (don't plan to use for a bit)
        self.quote_time = datetime.now() #crypto quotes don't seem to come with a timestamp (TODO:revisit to check if it changes)

        return


    #Info methods
    def general_info(self):
        self.get_quote()  # update for most current price

        print '\n__________General Info for {}___________'.format(self.name)
        print 'Code: {}'.format(self.code)
        print '# Owned: {}'.format(self.quantity_total)
        print 'Avg Buy Cost: ${}'.format(self.avg_cost_per_coin)
        if self.quantity_total >0:
            print 'Return:       ${}'.format(self.mark_price*self.quantity_total - self.avg_cost_per_coin*self.quantity_total)

        print '----------------------------------\n'


        #print currency







if __name__ == "__main__":
    #Setup
    my_trader = Robinhood()

    #login
    my_trader.login(username=config.USERNAME, password=config.PASSWORD)

    """
    instrument = dict(my_trader.instruments('BTH'))
    print instrument
    agen = Stock(my_trader, instrument)
    agen.general_info()
    print '------------------------'
    """
    #agen.all_info()
    #agen.quote_info()

    port = Portfolio(my_trader)



    holdings =  crypto_porfolio(my_trader)
    holdings.general_info()