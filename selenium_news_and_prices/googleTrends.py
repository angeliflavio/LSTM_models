# Google Trends
# repository at https://github.com/GeneralMills/pytrends

from pytrends.request import TrendReq
import fix_yahoo_finance as fyf


# connect to google trends
pytrends = TrendReq(hl='en-US', tz=360)
# build payload
kw_list=['unicredit']
pytrends.build_payload(kw_list=kw_list, cat=0, timeframe='all', geo='', gprop='')
# get interest over time
interest_over_time=pytrends.interest_over_time()


# function to compare the price of a stock with Google Trend of a keyword
def compare_stock_trend(stock,keyword):
    pytrends.build_payload(kw_list=[keyword], cat=0, timeframe='all', geo='', gprop='')
    gtrend=pytrends.interest_over_time()
    gtrend=gtrend[keyword]
    stock=fyf.download(stock,start='1980-01-01')
    stock=stock['Adj Close']
#    compare=stock.to_frame().join(gtrend)
    stock.plot()
    gtrend.plot()

compare_stock_trend('UCG.MI','volatility')    



pytrends.build_payload(kw_list=['volatility'], cat=0, timeframe='all', geo='', gprop='')
gtrend=pytrends.interest_over_time()
gtrend=gtrend['volatility']
gtrend.plot()
