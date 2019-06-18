# script to read news from Bloomberg (only title and summary)
# using requests to loop through all pages

import time
import datetime
from bs4 import BeautifulSoup
import requests
from sentiment import get_sentiment
import pandas as pd
import fix_yahoo_finance as fyf
import random
from functions import dateto5minutes

# ask stock code and date
search=input('Search for: ')
date_limit=input('Search back to (yyyy-mm-dd): ')
date_limit=datetime.datetime.strptime(date_limit,"%Y-%m-%d")

# function to insert time.sleep() and print the passing time
def waiting_function():
    for x in range(random.randint(10,30)):
        print(x)
        time.sleep(1)

# loop through all pages clicking next button
def get_articles():
    d=[]  # empty list to store all articles
    n=0   # count pages (the while loop starts from this page)
    while True: 
        print('\nGetting page',n)        
        waiting_function()           # wait a random time between each page
        try:
            html=requests.get('https://www.bloomberg.com/search?query='+search+'&sort=time:desc&endTime=2018-03-26T15:38:06.306Z&page='+str(n)).content
        except:
            print('Page link not working')
            continue
        n+=1
        soup=BeautifulSoup(html,'lxml')
        time.sleep(2)
        arts=soup.find_all('div',{'class':'search-result'})
        for article in arts:
            title=article.find('h1').text  
            t=article.find('time')['datetime']
            t=datetime.datetime.strptime(t,"%Y-%m-%dT%H:%M:%S+00:00")
            if t < date_limit:
                print('\n------\nDate limit reached')
                return(d)
            summary=article.find('div',{'class':'search-result-story__body'}).text
            link=article.find('h1').find('a')['href']
            title_polarity=round(get_sentiment(title),4)
            summary_polarity=round(get_sentiment(summary),4)
            d.append({'date':t, 'title':title, 'summary':summary, 'link':link, 'title_polarity':title_polarity, 'summary_polarity':summary_polarity})
            print('\n',len(d),t,title) 
            print('Title:',title_polarity,'\tSummary:',summary_polarity)
            
db=get_articles()

# transform list of dictionaries into a dataframe
df=pd.DataFrame(db).set_index('date')
df=df.sort_index(ascending=True)
df.to_csv('C:\\Users\\BTData\\Desktop\\selenium\\sentimentData\\intesa_articles_2010-2018.csv')
# average sentiment for articles on the same day
df['data']=df.index.date
df=df.groupby('data').mean()
df.index=pd.DatetimeIndex(df.index)
# convert time index to 5 minutes
#df['data']=[dateto5minutes(x) for x in df.index]
#df=df.groupby('data').mean()   # average observations with same time

# apply moving average to polarity
def make_average(data,ma=10): 
    data['polarity']=data[['title_polarity','summary_polarity']].mean(axis=1)        
    data['ma_title_polarity']=data[['title_polarity']].rolling(ma).mean()
    data['ma_summary_polarity']=data[['summary_polarity']].rolling(ma).mean()
    data['ma_polarity']=data[['polarity']].rolling(ma).mean()
    data['cum_title_polarity']=data['title_polarity'].cumsum()
    data['cum_summary_polarity']=data[['summary_polarity']].cumsum()
    data['cum_polarity']=data[['polarity']].cumsum()
    return(data)   
    
df=make_average(df,ma=50)

# plot polarity
df[['ma_polarity','ma_title_polarity','ma_summary_polarity']].plot(title=search,subplots=True)    
df[['cum_polarity','cum_title_polarity','cum_summary_polarity']].plot(title=search,subplots=True)    


# get stock prices and merge with sentiment data
stock='ISP.MI'
italian_stocks=pd.read_csv("C:\\Users\\BTData\\Desktop\\selenium\\italiaR\\italianStocks.csv")
prices=italian_stocks.loc[italian_stocks['id']==stock]   # get stock prices from csv file uploaded above
prices=prices.set_index(pd.DatetimeIndex(prices['Date']))
prices=prices.drop(['Close','Volume','id','Date'],axis=1)
prices.columns=['Open','High','Low','Close']
#prices=prices.loc['2010':]
prices[['Close']].plot() 
# merge stock prices with sentiment data and compare (for daily data)
compare=df.join(prices[['Close']],how='outer')
compare=compare.fillna(method='ffill')
   

# get 5 minutes unicredit stock price and merge with sentiment data
dateparse=lambda x: datetime.datetime.strptime(x,'%d/%m/%y %H:%M:%S')
prices=pd.read_csv("C:\\Users\\BTData\\Desktop\\selenium\\intraday_stock_prices\\unicredit5m.txt", 
                   sep='|',skiprows=1,parse_dates=[[0,1]], date_parser=dateparse)
prices=prices.set_index('DATA_ORA')
prices.columns=['Open','High','Low','Close','Volume']
prices['Close'].plot()
# merge stock price with sentiment data
compare=pd.merge(prices['Close'].to_frame(),df,left_index=True,right_index=True,how='left')
compare=compare.fillna(method='ffill')


# calculate n days return, n days standard deviation and correlations with sentiment
compare['nextDayReturn']=compare['Close'].pct_change().shift(-1)
target_window=10
compare['nextNdaysReturn']=compare['Close'].pct_change(target_window).shift(-target_window)   # return over the following n days
# N days in the future standard deviation, as alternative target instead of up/down return
compare['nextNdaysStd']=compare['nextDayReturn'].rolling(target_window).std().shift(-target_window)
# calculate correlations
index=['title_polarity','summary_polarity','ma_title_polarity',
       'ma_summary_polarity','polarity','ma_polarity',
       'cum_polarity','cum_title_polarity','cum_summary_polarity']
columns=['Close','nextDayReturn','nextNdaysReturn','nextNdaysStd']
corr_df=pd.DataFrame(index=index,columns=columns)
for polarity in index:
    for column in columns:
        corr_df[column][polarity]=compare[column].corr(compare[polarity]) 
print(corr_df)

# plot
year='2010'
compare.loc[year:][['title_polarity','summary_polarity','polarity','Close','nextNdaysStd']].plot(subplots=True,title='Polarity')
compare.loc[year:][['ma_title_polarity','ma_summary_polarity','ma_polarity','Close','nextNdaysStd']].plot(subplots=True,title='Average Polarity')
compare.loc[year:][['cum_polarity','cum_title_polarity','cum_summary_polarity','Close','nextNdaysStd']].plot(subplots=True,title='Average Polarity')
compare.plot.scatter('ma_polarity','nextNdaysReturn')
compare.plot.scatter('ma_polarity','nextNdaysStd')


# write data into a csv, which ca be uploaded on Google Colab
#provv=compare.drop(['link','summary','title'],axis=1)
compare.to_csv('C:\\Users\\BTData\\Desktop\\selenium\\sentimentData\\tenaris_sentiment.csv')
compare.to_csv('C:\\Users\\BTData\\Desktop\\selenium\\sentimentData\\ucg_sentiment2011.csv')
compare.to_csv('C:\\Users\\BTData\\Desktop\\selenium\\sentimentData\\ucg_sentiment_5minutes.csv')


## read 2010-2018 data from file and merge with 2005-2009
#compare2=pd.read_csv('C:\\Users\\BTData\\Desktop\\selenium\\sentimentData\\ucg_sentiment.csv',index_col=0,parse_dates=True)
#df2=compare2[['summary_polarity','title_polarity']].dropna()
#df2.head()
#df3=pd.concat([df,df2])
#df3.plot(subplots=True)





# transform polarity columns into categorical type
compare2=compare.copy()
s=['summary_polarity','title_polarity','polarity','ma_title_polarity','ma_summary_polarity','ma_polarity']
s_new=[x+'_categorical' for x in s]
def quantile_cut(x):
    groups=pd.qcut(x,4,duplicates='drop')
    return(groups)
compare2[s_new]=compare2[s].apply(quantile_cut)
# group by polarity and analyse average Return and Std
for x in s_new:
    print('\n',compare2.groupby(x)['nextNdaysReturn'].mean())
    print(compare2.groupby(x)['nextNdaysStd'].mean())

