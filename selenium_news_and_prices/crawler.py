# https://datarebellion.com/blog/quick-guide-to-installing-selenium/
# script to download financial series from Yahoo Finance
# csv files are downloaded into a selected folder

from selenium import webdriver
import os
import pandas as pd
import time

# function to get data from yahoo finance
def getdata(stock, sleeptime,folder_name):
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : folder_path}
    chrome_options.add_experimental_option('prefs', prefs)
    browser = webdriver.Chrome(chrome_options=chrome_options)
    url='https://finance.yahoo.com/quote/'+stock+'/history'
    browser.get(url)
    
    before=os.listdir(folder_path)
    
    # find element using Xpath
    daterange=browser.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/span/input')
    daterange.click()
    time.sleep(2)
    maxdate=browser.find_element_by_xpath("//span[text()='Max']")
    maxdate.click()
    time.sleep(2)
    done=browser.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/div[3]/button[1]/span')
    done.click()
    time.sleep(2)
    apply=browser.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button/span')
    apply.click()
    time.sleep(2)
    download=browser.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a')
    download.click()    
    time.sleep(sleeptime)
    browser.close()

    # find name of file downloaded
    after=os.listdir(folder_path)
    change=set(after)-set(before)
    
    # read csv file 
    if len(change) == 1:
        file_name = change.pop() #file name as string
        stock=pd.read_csv(folder_path+'\\'+file_name)
        print(stock.head())
    else:
        print("More than one file or no file downloaded",change)

# ask list of stocks
lista=input('Enter stocks to download (UCG.MI,SPY,...): ')
stocks=[x.strip() for x in lista.split(',')]

# create folder where all files will be stored
print('\nEnter name and path to create folder where all files will be downloaded.')
path=input('Path:')
folder_name=input('Name:')
folder_path=path+'\\'+folder_name
os.mkdir(path+'\\'+folder_name)


# loop through all stocks to download historical data
for stock in stocks:
    print('\nDownloading ',stock)
    getdata(stock,10,folder_name)
    
# check if all stocks are present in downloads
downloaded=os.listdir(folder_path)  
print('\nSlow downloading for incomplete files.')
for stock in stocks:
    if stock+'.csv' not in downloaded:
        print(stock)
        getdata(stock,20,folder_name)

# remove incomplete files
for file in os.listdir(folder_path):
    if file.endswith('.tmp'):
        print('Removing ',file)
        os.remove(folder_path+'\\'+file)




'''
A2A.MI,ATL.MI,AZM.MI,BGN.MI,BMED.MI,
          BAMI.MI,BPE.MI,BRE.MI,BZU.MI,CPR.MI,
          CNHI.MI,ENEL.MI,ENI.MI,EXO.MI,RACE.MI,
          FCA.MI,FBK.MI,G.MI,ISP.MI,IG.MI,
          LDO.MI,LUX.MI,MS.MI,MONC.MI,
          PST.MI,PRY.MI,REC.MI,SPM.MI,SFER.MI,
          SRG.MI,STM.MI,TIT.MI,TEN.MI,TRN.MI,
          UBI.MI,UCG.MI,UNI.MI,US.MI,YNAP.MI
'''
