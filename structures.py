

from Robinhood import Robinhood
import config
import pandas as pd
from datetime import time, datetime
from bokeh.plotting import figure, output_file, show


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
            self.stocks.append(Stock(self, self.trader, instrument))


        for stock in self.stocks:
            print stock.general_info()


    def stock_handles(self):
        stock_dict = dict()
        for stock in self.stocks:
            stock_dict[stock.symbol] = stock
        print stock_dict
        return stock_dict


    def all_past_orders(self):
        """
        Gets past order history for STOCKS, won't return crypto trades
        :return: df with all past orders
        """

        print "~~~~ Getting Trade History ~~~~"
        #Get raw past order output from Robinhood
        past_orders_raw = my_trader.order_history()

        # Fetch past orders
        results = past_orders_raw['results']

        # reformat into a df
        order_history_pd = pd.DataFrame(data=results)
        order_history_pd.columns = order_history_pd.columns.astype(str)

        # insert column that will hold symbol names for each trade
        order_history_pd.insert(0, 'symbol', None)

        # Use instrument url to get the stock symbol for each trade and insert it into the df
        for row in order_history_pd.iterrows():
            instrument = my_trader.get_url(row[1]['instrument'])
            order_history_pd.at[row[0], 'symbol'] = instrument['symbol']

        return order_history_pd




class Stock:
    def __init__(self, portfolio, my_trader, instrument):
        self.portfolio = portfolio
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

        #Other Info
        self.last_extened_hours_trade_price = quote['last_extended_hours_trade_price'] # for estimating return when markets are closed

        #Quote Update Time (don't plan to use for a bit)
        self.quote_time = datetime.strptime(str(quote['updated_at']),'%Y-%m-%dT%H:%M:%SZ') #Assuming it will always come as UTC (Z)

        return True



    def plot_historical_quotes(self, interval = '5minute', span = 'week', fig_title='', show_plot = True):
        '''
        Creates a bokeh plot of the historical quotes for this stock. Useful for then overlaying other info (like
        buy/sell points, etc.)
        :param data:
        :param data_type: Historical quotes, open-close, purchasing over historical prices
        :return: Bokeh plot of historical quotes
        '''

        #create generic figure name if one wasn't passed
        if fig_title == '':
            fig_title = "{} - Historical Quotes".format(self.symbol)


        #Get historical quotes
        self.historical_quotes_df = self.historical_quotes(interval=interval, span=span)

        print "********* Plotting Historical Quotes for {} ***********".format(self.symbol)

        #Do the plotting
        p = figure(title=fig_title, plot_width=1000, plot_height=500, x_axis_type = 'datetime')
        p.line(x= self.historical_quotes_df['begins_at'].values, y=self.historical_quotes_df['high_price'].values, color='blue', legend='High Price')
        p.line(x=self.historical_quotes_df['begins_at'].values, y=self.historical_quotes_df['low_price'].values, color='red', legend='Low Price')

        p.yaxis.axis_label = "Price (Dollar)"
        p.xaxis.axis_label = "Date"

        output_file('{}-Historical Quotes Plot.html'.format(self.symbol))

        if show_plot:
            show(p)

        return p

    def update_past_orders(self):
        """
        Fetches past orders of this stock and does some parsing to make accessing filled orders easier elsewhere
        :return:
        """

        #TODO: Implement a method to grab the order history for just one stock
        all_past_orders = self.portfolio.all_past_orders() #This is REALLY inefficient (takes forever)

        #Now pre-parse into commonly used categories
        self.past_orders = all_past_orders[all_past_orders['symbol']==self.symbol] #Past orders for only this stock
        self.filled_orders = self.past_orders[self.past_orders['state']=='filled'] #Only orders that were filled (not canceled)

        return True


    def plot_purchase_vs_price(self):
        """
        Plots the buy & Sell order history of this stock overlaid on the historical quote data to get a quick guage of
        buy vs sell timing.

        :output: Bokeh Plot. Shows it in a browser and saves it.
        :return: True
        """
        #Fetch most up to date past orders
        self.update_past_orders()

        #Now parse out sell and buy orders into their own dataframes
        buy_orders = pd.DataFrame(columns=['datetime','price'])
        sell_orders = pd.DataFrame(columns=['datetime', 'price'])

        for order in self.filled_orders.iterrows():
            order = order[1]

            if order['side'] == 'buy': #Buy Orders
                executions = order['executions'][0]
                price = float(executions['price'])
                timestamp = executions['timestamp']

                #append to buy orders df
                buy_orders = buy_orders.append({'datetime': timestamp,
                                   'price': price}, ignore_index=True)

            elif order['side'] == 'sell': #Sell Orders
                executions = order['executions'][0]
                price = float(executions['price'])
                timestamp = executions['timestamp']

                #append to sell orders df
                sell_orders = buy_orders.append({'datetime': timestamp,
                                   'price': price}, ignore_index=True)

        #convert timestamps to datetime for plotting
        buy_orders['datetime'] = pd.to_datetime(buy_orders['datetime'])
        sell_orders['datetime'] = pd.to_datetime(buy_orders['datetime'])


        #PLOTTING
        #Start by creating plot of historical Quotes to build off of
        p = self.plot_historical_quotes(interval='day',
                                        span='3month',
                                        fig_title='{} - Buy vs Sell Plot'.format(self.symbol),
                                        show_plot=False)

        #now plot buy and sell orders over the historical quotes data
        p.scatter(x=buy_orders['datetime'].values, y=buy_orders['price'].values, color='black', legend='Buy')
        p.scatter(x=sell_orders['datetime'].values, y=sell_orders['price'].values, color='green', legend='Sell')
        p.legend

        #save and show the plot
        output_file('{}-buy sell plot.html'.format(self.symbol))
        show(p)

        return True



    def historical_quotes(self, interval = '5minute', span = 'week'):
        '''

        :param num_months: number of months to fetch
        :return:
        '''

        #Grab historical data
        history = my_trader.get_historical_quotes(self.symbol, interval=interval, span = span, bounds='regular')


        #sort and reformat historicals
        historicals = history['historicals']

        hist_pd = pd.DataFrame.from_dict(historicals)
        hist_pd.columns = hist_pd.columns.astype(str)
        hist_pd['begins_at'] = pd.to_datetime(hist_pd['begins_at'])

        #save log
        #TODO: add time span to naming
        hist_pd.to_csv('/Users/samvarney/PycharmProjects/robinhood_trading/data/quote_historicals/{}_hist_quotes.csv'.format(self.symbol))

        return hist_pd



    # Methods for summarizing information on stock
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

    """
    past_orders = port.all_past_orders()
    for row in past_orders.iterrows():
        data = row[1]
        if data['state'] == 'filled':
            print data['executions']
      """




    stock_dict = port.stock_handles()
    for key in stock_dict:
        stock = stock_dict[key]
        #stock.plot_historical_quotes()
        stock.plot_purchase_vs_price()



    #holdings =  crypto_porfolio(my_trader)
    #holdings.general_info()