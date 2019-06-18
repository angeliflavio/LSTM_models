# script to read news from Yahoo Finance

from selenium import webdriver
import time
import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
from sentiment import get_sentiment
import fix_yahoo_finance as fyf


# get yahoo finance full page, scrolling down to have all news
stock=input('Enter stock code: ')
driver=webdriver.Chrome()
driver.get('https://finance.yahoo.com/quote/'+stock+'/news')
lastHeight=driver.execute_script("return Math.max(document.documentElement.scrollHeight," + "document.body.scrollHeight,document.documentElement.clientHeight)")
n=0
while True:
    driver.execute_script("window.scrollTo(0,Math.max(document.documentElement.scrollHeight," + "document.body.scrollHeight,document.documentElement.clientHeight));")
    time.sleep(2)
    newHeight=driver.execute_script("return Math.max(document.documentElement.scrollHeight," + "document.body.scrollHeight,document.documentElement.clientHeight)")
    n+=1
    print('loading page ',n)
    if newHeight==lastHeight:
        print('bottom reached.')
        break
    lastHeight=newHeight

# get html and find all news articles, storing them as list
html=driver.page_source
soup=BeautifulSoup(html,'lxml')
articles=[]
trova=soup.find_all('a',{'class':'Fw(b) Fz(20px) Lh(23px) LineClamp(2,46px) Fz(17px)--sm1024 Lh(19px)--sm1024 LineClamp(2,38px)--sm1024 Td(n) C(#0078ff):h C(#000)'})
for tag in trova:
    link=tag.get('href')
    if link.startswith('http'):
        continue
    print('\n',tag.text)
    article_link='https://finance.yahoo.com'+link
    print(article_link)
    articles.append(article_link)    

# get date and text of all articles, save them as list of dictionaries
d=[]
for art in articles:
    try:
        html=requests.get(art).content
    except:
        print('Page not working',art)
        continue
    soup=BeautifulSoup(html,'lxml')
    t=soup.find('time')['datetime']
    t=datetime.datetime.strptime(t,"%Y-%m-%dT%H:%M:%S.%fZ")
    title=soup.find('h1',{'itemprop':'headline'}).text
    try:
        testo=soup.find('article',{'itemprop':'articleBody'}).text
    except:
        try:
            testo=soup.find('p',{'class':'canvas-text Mb(1.0em) Mb(0)--sm Mt(0.8em)--sm canvas-atom'}).text
        except:
            testo=''
            print('\ntext not working',art)
    title_sentiment=round(get_sentiment(title),4)
    text_sentiment=round(get_sentiment(testo),4)
    d.append({'date':t,'title':title,'text':testo,'title_sentiment':title_sentiment,'text_sentiment':text_sentiment})
    print('\n',t,title,title_sentiment,text_sentiment)


# convert articles data into a dataframe
df=pd.DataFrame(d).set_index('date')
df=df.sort_index(ascending=True)    #ascending order
# average sentiment for articles on the same day
df['data']=df.index.date
df=df.groupby('data').mean()
# calculate moving average on sentiment
days=10
df['ma_title_sentiment']=df[['title_sentiment']].rolling(days).mean()
df['ma_text_sentiment']=df[['text_sentiment']].rolling(days).mean()

# plot
df[['title_sentiment','text_sentiment']].plot(title='Sentiment',subplots=True)    
 
# get stock prices
stock='UCG.MI'
italian_stocks=pd.read_csv("C:\\Users\\BTData\\Desktop\\selenium\\italiaR\\italianStocks.csv")
prices=italian_stocks.loc[italian_stocks['id']==stock]   # get stock prices from csv file uploaded above
prices=prices.set_index(pd.DatetimeIndex(prices['Date']))
prices=prices.drop(['Close','Volume','id','Date'],axis=1)
prices.columns=['Open','High','Low','Close']
prices.head()
prices[['Close']].plot() 
   
# merge stock prices with news sentiment data
compare=df.join(prices[['Close']],how='outer')
compare=compare.fillna(method='ffill')
# n days return
compare['nextDayReturn']=compare['Close'].pct_change().shift(-1)
target_window=10
compare['nextNdaysReturn']=compare['Close'].pct_change(target_window).shift(-target_window)   # return over the following n days
# N days in the future standard deviation, as alternative target instead of up/down return
compare['nextNdaysStd']=compare['nextDayReturn'].rolling(target_window).std().shift(-target_window)


# calculate correlations
index=['title_sentiment','text_sentiment','ma_title_sentiment','ma_text_sentiment',]
columns=['Close','DailyReturn','NdaysReturn','NdaysStd']
corr_df=pd.DataFrame(index=index,columns=columns)
for polarity in index:
    for column in columns:
        corr_df[column][polarity]=compare[column].corr(compare[polarity])
print(corr_df)

# plot
year='2017-05-11'
compare.loc[year:][['title_sentiment','text_sentiment','Close']].plot(subplots=True,title='Sentiment')
compare.loc[year:][['ma_title_sentiment','ma_text_sentiment','Close']].plot(subplots=True,title='Average Sentiment')
