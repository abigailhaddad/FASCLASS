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
    url = f'https://www.bing.com/search?q={term}%20AND%20"position%20description"'
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
    
def scrapePD(link):
    page = urlopen(link)
    html_bytes = page.read()
    soup = BeautifulSoup(html_bytes, 'html.parser')
    text=soup.get_text().replace("\n","").replace("\t","").replace("\r","").split("POSITION DESCRIPTION")[1]
    text=ILLEGAL_CHARACTERS_RE.sub(r'',text)
    text=text.encode('utf-8', 'replace').decode()
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
            dictOfPDs[PDnumber]=scrapePD(link)
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
    
def cleanFailedLinks(failedLinks):
    dictText={}
    for link in failedLinks:
        try:
            dictText[link]=scrapePD(link)
        except:
            dictText[link]=""
    listForDF = list(zip(dictText.keys(), dictText.values()))
    PDTextFailed = pd.DataFrame(listForDF, columns = ['CCPO ID', 'PD Text'])
    return(PDTextFailed)
    
def cleanNoLinks(noLinks):
    dictText={}
    for term in noLinks:
        try:
            topResult=getGoogleLinks(term)
            text=scrapePD(topResult)
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
    print(f'there are {len(failedLinks)} failedlinks')
    cleanerFailedLinks=["ht"+i.split("ht")[1].split("%3D")[0]+"%3D" for i in failedLinks]
    #ok so that one worked
    PDTextFailed=cleanFailedLinks(cleanerFailedLinks)
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


if __name__ == "__main__":
    try:
        dfPDs=pd.read_excel("undoneIDs.xlsx", engine='openpyxl')
    except:
        #if you have the initial data set this was derived from with the actual people
        #then you can generate the undoneIDs xlsx
        #df=readData('CP DATA 22SEP2021.xlsx')
        #df=genID(df)
        dfPDs=pd.read_excel("exportIDs.xlsx", engine='openpyxl')
        dfPDs.to_excel("undoneIDs.xlsx", index=False)
    getPDLookups(dfPDs)
        

#dfPeople=readData('CP DATA 22SEP2021.xlsx') 
#merged=dfPeople.merge(df, left_on='CCPO ID', right_on='CCPO ID')
#hasCP36=merged.loc[merged['cleanText'].astype(str).str.contains("CP:36")]

