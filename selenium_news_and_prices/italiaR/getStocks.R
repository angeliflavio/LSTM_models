# download and save as csv file for Google Colab notebook
# saved into italiaR


lista=c('A2A.MI','ATL.MI','AZM.MI','BGN.MI','BMED.MI',
       'BAMI.MI','BPE.MI','BRE.MI','BZU.MI','CPR.MI',
       'CNHI.MI','ENEL.MI','ENI.MI','EXO.MI','RACE.MI',
       'FCA.MI','FBK.MI','G.MI','ISP.MI','IG.MI',
       'LDO.MI','LUX.MI','MS.MI','MONC.MI',
       'PST.MI','PRY.MI','REC.MI','SPM.MI','SFER.MI',
       'SRG.MI','STM.MI','TIT.MI','TEN.MI','TRN.MI',
       'UBI.MI','UCG.MI','UNI.MI','US.MI','YNAP.MI')

italia <- list()
for (stock in lista){
  titolo <- getSymbols(stock,auto.assign = FALSE,from='1950-01-01')
  names(titolo) <- c('Open','High','Low','Close','Volume','Adjusted')
  df <- as.data.frame(titolo,row.names = NULL)
  df$Date <- index(titolo)
  df$id <- stock
  italia[[stock]] <- df
}
# aggregate stocks into one df  
italian_stocks <- data.frame()
for (x in 1:length(italia)){
  italian_stocks <- rbind(italian_stocks,italia[[x]])
}


# save as csv
write.csv(italian_stocks, file = "C:\\Users\\BTData\\Desktop\\selenium\\italiaR\\italianStocks.csv",row.names=FALSE)




