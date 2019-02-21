from Robinhood import Robinhood
import time
import config

#Setup
my_trader = Robinhood()

#login
my_trader.login(username=config.USERNAME, password=config.PASSWORD)


#Get stocks owned
securities = my_trader.securities_owned()
print '\n\n'
for key in securities['results']:

    instrument = my_trader.get_url(key['instrument'])  # get symbol of stock
    name = instrument['symbol']
    news = my_trader.get_news(name)

    #Get price
    quote = my_trader.quote_data(name)
    last_price = float(quote['last_trade_price'])
    price_bought = float(key['pending_average_buy_price'])
    print name + ' - Current Price: $' + str(last_price) + '. (Bought: ' + str(price_bought) + ')'

    for article in news['results']:
        article = dict(article)
        print '--------------------------------------------------'
        print article['title']
        print article['url']
        #print article['summary']

    print '--------------------------------------------------'
    print '--------------------------------------------------'
    print '\n\n'

    #now get out position info
    quantity_owned = float(key['quantity'])
    quote = my_trader.quote_data(name)