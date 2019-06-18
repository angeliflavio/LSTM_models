# script to read news from Bloomberg
# using seenium to click Next page

from selenium import webdriver
import time
import datetime
from bs4 import BeautifulSoup
import requests
from sentiment import get_sentiment
import pandas as pd
import matplotlib.pyplot as plt
import fix_yahoo_finance as fyf


# ask stock code and date
search=input('Search for: ')
date_limit=input('Search back to (yyyy-mm-dd): ')
date_limit=datetime.datetime.strptime(date_limit,"%Y-%m-%d")

# get yahoo finance full page, scrolling down to have all news
driver=webdriver.Chrome()
driver.get('https://www.bloomberg.com/search?query='+search)
time.sleep(2)

# click advanced search
driver.find_element_by_xpath('//*[@id="content"]/div/section/section[1]/div[3]/div[1]/a/label').click()
time.sleep(10)
# click sort by Newest
driver.find_element_by_xpath('//*[@id="search-sort-options__select-id"]/option[@value="time:desc"]').click()
time.sleep(2)

# loop through all pages clicking next button
def get_articles():
    d=[]  # empty list to store all articles
    n=1   # count pages
    while True: 
        driver.find_element_by_xpath('//a[@class="content-next-link"]').click()
        time.sleep(3)
        n+=1
        print('\n-------\nClick next --> page ',n)
        url=driver.current_url
        print(url,'\n')
        html=driver.page_source
        soup=BeautifulSoup(html,'lxml')
        arts=soup.find_all('div',{'class':'search-result'})
        for article in arts:
            title=article.find('h1').text  
            t=article.find('time')['datetime']
            t=datetime.datetime.strptime(t,"%Y-%m-%dT%H:%M:%S+00:00")
            if t < date_limit:
                print('\n------\nDate limit reached')
                driver.close()
                return(d)
            summary=article.find('div',{'class':'search-result-story__body'}).text
            link=article.find('h1').find('a')['href']
            try:
                html=requests.get(link).content
                soup=BeautifulSoup(html,'lxml')         
                testo=soup.find('div',{'class':'body-copy fence-body'}).text  
                title_polarity=round(get_sentiment(title),4)
                summary_polarity=round(get_sentiment(summary),4)
                text_polarity=round(get_sentiment(testo),4)
                d.append({'date':t, 'title':title, 'summary':summary, 'link':link, 'title_polarity':title_polarity, 'summary_polarity':summary_polarity, 'text_polarity':text_polarity})
            except:
                print('\nLink not working: ', link)
                continue
            print('\n',len(d),t,title) 
            print('Title:',title_polarity,'\tSummary:',summary_polarity,'\tText:',text_polarity)
db=get_articles()

# make dataframe and apply moving average to polarity
def make_df(db,ma=10): 
    df=pd.DataFrame(db).set_index('date')
    df=df.sort_index(ascending=True)
    df['polarity']=df[['title_polarity','summary_polarity','text_polarity']].mean(axis=1)        
    df['ma_title_polarity']=df[['title_polarity']].rolling(ma).mean()
    df['ma_summary_polarity']=df[['summary_polarity']].rolling(ma).mean()
    df['ma_text_polarity']=df[['text_polarity']].rolling(ma).mean()
    df['ma_polarity']=df[['polarity']].rolling(ma).mean()
    return(df)    
df=make_df(db,ma=30)
# plot polarity
df[['ma_polarity','ma_title_polarity','ma_summary_polarity','ma_text_polarity']].plot(title=search,subplots=True)    


# get prices
stock='UCG.MI'
prices=fyf.download(stock,start='1980-01-01')
prices=prices.drop(['Close','Volume'],axis=1)
prices.columns=['Open','High','Low','Close']
prices.head()
prices[['Close']].plot()    
# merge data
compare=df.join(prices[['Close']],how='outer')
compare=compare.fillna(method='ffill')

# n days return
compare['DailyReturn']=compare['Close'].pct_change().shift(-1)
target_window=10
compare['NdaysReturn']=compare['Close'].pct_change(target_window).shift(-target_window)   # return over the following n days
# N days in the future standard deviation, as alternative target instead of up/down return
compare['NdaysStd']=compare['DailyReturn'].rolling(target_window).std().shift(-target_window)
# delta polarity
compare['delta_title_polarity']=compare['title_polarity'].diff()
compare['delta_summary_polarity']=compare['summary_polarity'].diff()
compare['delta_text_polarity']=compare['text_polarity'].diff()
compare['delta_polarity']=compare['polarity'].diff()

# correlations
index=['title_polarity','summary_polarity','text_polarity','ma_title_polarity',
       'ma_summary_polarity','ma_text_polarity','polarity','ma_polarity',
       'delta_title_polarity','delta_summary_polarity','delta_text_polarity']
columns=['Close','DailyReturn','NdaysReturn','NdaysStd']
corr_df=pd.DataFrame(index=index,columns=columns)
for polarity in index:
    for column in columns:
        corr_df[column][polarity]=compare[column].corr(compare[polarity])
print(corr_df)

# plot
year='2017'
compare.loc['2017':][['title_polarity','summary_polarity','text_polarity','polarity','Close']].plot(subplots=True,title='Polarity')
compare.loc['2017':][['ma_title_polarity','ma_summary_polarity','ma_text_polarity','ma_polarity','Close']].plot(subplots=True,title='Average Polarity')
compare.loc['2017':][['delta_title_polarity','delta_summary_polarity','delta_text_polarity','delta_polarity','Close']].plot(subplots=True,title='Delta Polarity')

