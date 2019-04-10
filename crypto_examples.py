from Classes import *
from Robinhood import Robinhood
import config

# Setup
my_trader = Robinhood()

# login
my_trader.login(username=config.USERNAME, password=config.PASSWORD)



holdings =  crypto_porfolio(my_trader)
holdings.general_info()

print my_trader.crypto_quote_data('BTCUSD')

for holding in holdings.holdings:
    if holding.name == 'Litecoin':
        ltc_holding = holding
        print holding.name


print ltc_holding.ask_price

print my_trader.buy_crypto('BTCUSD',
                             price=ltc_holding.ask_price,
                             quantity=10/ltc_holding.ask_price,
                             transaction='sell')