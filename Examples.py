from Classes import *
from Robinhood import Robinhood
import config

# Setup
my_trader = Robinhood()

# login
my_trader.login(username=config.USERNAME, password=config.PASSWORD)



#################################
# Looking at a single stock (AGEN used as example)
#################################
instrument = dict(my_trader.instrument('AGEN')[0]) #Get Robinhood Instrument Link

agen = Stock(trader=my_trader,
             instrument=instrument) #initialized Stock object using the instrument link

agen.general_info() #Print general info for this stock
agen.all_info() #print more detailed info
agen.quote_info() #Get latest quote details

#Generate historical quote and buy/sell history plots
agen.plot_historical_quotes(interval='day', span='5year', fig_title='', show_plot=True)
agen.plot_purchase_vs_price()


#################################
# Operations using Portfolio Class
#################################

#Initialize the porfolio object (uses the stocks owned by the Robinhood Account used)
port = Portfolio(my_trader)


# Get Past Stock orders
past_orders = port.all_past_orders()


# Use Stock objects to generate historical quote and buy/sell history plots
stock_dict = port.stock_handles()
for key in stock_dict:
    stock = stock_dict[key]
    stock.plot_historical_quotes(interval = 'day', span = '5year', fig_title='', show_plot = True)
    stock.plot_purchase_vs_price()



#################################
# Cryptocurrency Usage (still bare bones)
#################################

holdings =  crypto_porfolio(my_trader)
holdings.general_info()