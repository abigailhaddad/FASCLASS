# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 09:20:19 2021
this is the version of my scraper that I use in PYTHONANYWHERE

the input is an excel file called "exportIDs.xlsx" which contains a DF with a column
called 'CCPO ID' which contains the position description numbers you want to look up

the output is a list of CSV and XLSX files with corresponding position description text
split into groups of 10,000
@author: HaddadAE
"""


import os
import pandas as pd
from googlesearch import search
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from datetime import datetime


os.chdir(os.getcwd().replace("code", "data"))

def readData(fileName):
    # you need to specify the engine depending on the versions of the libraries
    df=pd.read_excel(fileName, engine='openpyxl')
    return(df)
    
def genID(df):
    df['CCPO ID']=df['Ccpo Id']+df['CPCN']
    df[['CCPO ID']].drop_duplicates().to_excel("exportIDs.xlsx")
    return(df)
    
def getBing(term):
    url=f'https://www.bing.com/search?q=%22PD%23%3A+{term}%22&qs=n&form=QBRE&sp=-1&pq=%22pd%23%3A+desrpc004&sc=0-15&sk=&cvid=C439A0BB38304769B9BE279AB65424BC'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    #YOU WOuLDN'T THINK THIS USER AGENT VALUE IS IMPORTANT BUT IT ISSSSS
    response = requests.get(url,headers=headers) 
    return(response)
    
def getGoogleLinks(term):
    links=[]
    for j in search(term, num=10, stop=10, pause=2):
        links.append(j)
    links=[i for i in links if "search_fs_output" in i]
    return(links[0])
    
def getFASCLASSLinks(response):
    links=[]
    soup = BeautifulSoup(response.text, 'html.parser')
    anchors = soup.find_all("a")
    for anchor in anchors:
        if anchor is not None:
            try:
                if "acpol2.army.mil" in anchor["href"]:
                    links.append((anchor.getText(), anchor["href"])[1])
            except KeyError:
                continue    
    return(links)
    
def getRightLink(PDnumber):
    response=getBing(PDnumber)
    links=getFASCLASSLinks(response)
    findStr="search_fs_output"
    topResult=[j for j in links if findStr in j][0]
    return(topResult)
    
def scrapePD(link, PDnumber):
    page = urlopen(link)
    html_bytes = page.read()
    soup = BeautifulSoup(html_bytes, 'html.parser')
    text=soup.get_text().replace("\n","").replace("\t","").replace("\r","").split("POSITION DESCRIPTION")[1]
    text=ILLEGAL_CHARACTERS_RE.sub(r'',text)
    text=text.encode('utf-8', 'replace').decode()
    PD=text.split("PD#:", 1)[1].split("Sequence#", 1)[0].strip()
    if PD!=PDnumber:
        text=PDnumber
    else:
        pass
    return(text)

def writeOut(df):
    currenttime=datetime.now().strftime("%m%d%Y %H%M%S")
    df.to_excel(f"textScrape {currenttime}.xlsx")
    df.to_csv(f"textScrape {currenttime}.csv")
    dfPDs=pd.read_excel("undoneIDs.xlsx", engine='openpyxl')
    ###YOU HAVE TO SPECIFY THE ENGINE DEPENDING ON THE LIBRARY VERSION #s
    donePDNumbers=list(df['CCPO ID'])
    undonePD=dfPDs.loc[~dfPDs['CCPO ID'].isin(donePDNumbers)]
    undonePD[['CCPO ID']].to_excel("undoneIDs.xlsx", index=False)
    
def getPDLookups(dfPDs):
    dictOfPDs={}
    number=0   
    undonePDNumbers=list(dfPDs['CCPO ID'])
    for PDnumber in undonePDNumbers:
        number=number+1
        try:
            link=getRightLink(PDnumber)
        except:
            link=""
        try:
            dictOfPDs[PDnumber]=scrapePD(link, PDnumber)
        except:
            dictOfPDs[PDnumber]=link
        if number<100:
            print(number)
        if (number%100==0) and number!=0:
            print(number)
        if (number%10000==0) and number!=0:
            getCleanWrite(dictOfPDs)
            dictOfPDs={}
    getCleanWrite(dictOfPDs)
    
def cleanFailedLinks(failedLinks, PDnumbers):
    dictText={}
    for linkNo in range(0, len(failedLinks)):
        try:
            dictText[failedLinks[linkNo]]=scrapePD(failedLinks[linkNo], PDnumbers[linkNo])
        except:
            dictText[failedLinks[linkNo]]=""
    listForDF = list(zip(dictText.keys(), dictText.values()))
    PDTextFailed = pd.DataFrame(listForDF, columns = ['CCPO ID', 'PD Text'])
    return(PDTextFailed)
    
def cleanNoLinks(noLinks):
    dictText={}
    for term in noLinks:
        try:
            topResult=getGoogleLinks(term)
            text=scrapePD(topResult, term)
            dictText[term]=text
        except:
            dictText[term]=term
    listForDF = list(zip(dictText.keys(), dictText.values()))
    PDTextFailed = pd.DataFrame(listForDF, columns = ['CCPO ID', 'PD Text'])
    return(PDTextFailed)
    
   
def makeDF(PDText):
    listForDF = list(zip(PDText.keys(), PDText.values()))
    PDText = pd.DataFrame(listForDF, columns = ['CCPO ID', 'PD Text'])
    return(PDText)
    
def cleanBlankStragglers(df):
    failedLinks=list(df.loc[df["PD Text"].astype(str).str.contains("search_fs_output")]['PD Text'])
    failedPDs=list(df.loc[df["PD Text"].astype(str).str.contains("search_fs_output")]['CCPO ID'])
    print(f'there are {len(failedLinks)} failedlinks')
    cleanerFailedLinks=["ht"+i.split("ht")[1].split("%3D")[0]+"%3D" for i in failedLinks]
    #ok so that one worked
    PDTextFailed=cleanFailedLinks(cleanerFailedLinks, failedPDs)
    blanksCCPs= pd.Series(list(df.loc[df["PD Text"].astype(str).str.contains("search_fs_output")]['CCPO ID']))
    PDTextFailed['CCPO ID']= blanksCCPs
    keepdf=df.loc[~df['PD Text'].isin(failedLinks)]
    fixedBlank=pd.concat([keepdf[['CCPO ID', 'PD Text']],PDTextFailed])
    fixedBlank['Length']=fixedBlank['PD Text'].astype(str).str.len()
    noLinks=list(fixedBlank.loc[fixedBlank["Length"]<1000]['CCPO ID'])
    print(f'there are {len(noLinks)} noLinks')
    PDTextLinkFailed=cleanNoLinks(noLinks)
    PDTextLinkFailed['Length']=PDTextLinkFailed['PD Text'].astype(str).str.len()
    PDTextLinkWorked=PDTextLinkFailed.loc[PDTextLinkFailed['Length']>100][['CCPO ID', 'PD Text']]
    fixedBlank=fixedBlank.loc[~fixedBlank['CCPO ID'].isin(list(PDTextLinkWorked['CCPO ID']))]
    fixedMissingBlank=pd.concat([fixedBlank,PDTextLinkWorked])
    return(fixedMissingBlank)

def cleanText(string):
    try:
        cleanStart="PD#"+ string.split("PD#", maxsplit=1)[1]
        delChars=["xa0","'", "\\","}", "{", "}" ]
        for char in delChars:
            cleanStart=cleanStart.replace(char,"")
        cleanStart=cleanStart.replace("EXEMPTFLSA", "EXEMPT FLSA")
        cleanStart=cleanStart.replace("VARIES","VARIES ")
        cleanStart=cleanStart.replace("Sequence#"," Sequence#")
        cleanStart=cleanStart.replace("Citation", " Citation")
        cleanStart=cleanStart.replace("Classification", " Classification")
        cleanStart=cleanStart.replace("Organization Title", " Organization Title")
        cleanStart=cleanStart.replace("Command Code", " Command Code")
        cleanStart=cleanStart.replace("Agency:", " Agency:")
        cleanStart=cleanStart.replace("GS-", " GS-")
        cleanStart=cleanStart.replace("GG-", " GG-")
        cleanStart=cleanStart.replace("POSITION INFORMATION", " POSITION INFORMATION ")
        cleanStart=cleanStart.replace("Mission Category:", " Mission Category: ")
        cleanStart=cleanStart.replace("Installation:", " Installation: ")
        return(cleanStart)
    except:
        return()

def getCleanWrite(dictOfDF):
    df=makeDF(dictOfDF)
    df=cleanBlankStragglers(df)
    df['PD Text']=df['PD Text'].apply(cleanText)
    writeOut(df)

def runAll():    
    try:
        dfPDs=pd.read_excel("undoneIDs.xlsx", engine='openpyxl').head(100)
    except:
        #if you have the initial data set this was derived from with the actual people
        #then you can generate the undoneIDs xlsx
        #df=readData('CP DATA 22SEP2021.xlsx')
        #df=genID(df)
        dfPDs=pd.read_excel("exportIDs.xlsx", engine='openpyxl')
        dfPDs.to_excel("undoneIDs.xlsx", index=False)
    getPDLookups(dfPDs)
                            
def getPD(text):
    try:
        PD=text.split("PD#:", 1)[1].split("Sequence#", 1)[0].strip()
        return(PD)
    except:
        return()
        
runAll()
"""      
test=pd.read_csv("aggregatePD.csv")
test['PD Number']=test['PD Text'].apply(getPD)
test=test.loc[test['PD Number'].astype(str)==test['CCPO ID'].astype(str)]

for file in  ['textScrape 10302021 000246.xlsx','textScrape 10302021 015403.xlsx', 
              'textScrape 11012021 172607.xlsx' ,'textScrape 11022021 160804.xlsx']:
    df=pd.read_excel(file)
    test=pd.concat([test,df])
test['PD Number']=test['PD Text'].apply(getPD)    
goods=list(test.loc[test['PD Number'].astype(str)==test['CCPO ID'].astype(str)]['CCPO ID'].unique())
bads=list(test.loc[test['PD Number'].astype(str)!=test['CCPO ID'].astype(str)]['CCPO ID'].unique())
realBads=[i for i in bads if i not in goods]

final=test.loc[test['PD Number'].astype(str)==test['CCPO ID'].astype(str)].drop_duplicates()
badDF=pd.DataFrame(data=realBads, columns=['CCPO ID'])
forExport=pd.concat([final, badDF])

forExport.to_csv("aggregatePD.csv")
#undoneIDs=pd.DataFrame(data=realBads, columns=['CCPO ID'])
#undoneIDs.to_excel("undoneIDs.xlsx")
"""