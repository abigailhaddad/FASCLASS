# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 09:20:19 2021
having some issues with RAM limits; need to split this off. 
@author: HaddadAE
"""

import os
import pandas as pd
#from googlesearch import search
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urlencode, urlparse, parse_qs
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
#from googlesearch import search
from datetime import date, datetime

os.chdir(os.getcwd().replace("code", "data"))

def readData(fileName):
    df=pd.read_excel(fileName)
    return(df)
    
def genID(df):
    df['CCPO ID']=df['Ccpo Id']+df['CPCN']
    df[['CCPO ID']].drop_duplicates().to_excel("exportIDs.xlsx")
    return(df)
    
def getBing(term):
    url = f'https://www.bing.com/search?q={term}%20AND%20"position%20description"'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    #YOU WOuLDN"T THINK THIS USER AGENT VALUE IS IMPORTANT BUT IT ISSSSS
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

def writeOut(PDText):
    listForDF = list(zip(PDText.keys(), PDText.values()))
    PDText = pd.DataFrame(listForDF, columns = ['CCPO ID', 'PD Text'])
    PDText.to_excel("textScapePD.xlsx")
    PDText.to_csv("textScapePD.csv")
    return(PDText)

def getPDLookups(dfPDs, initialDF):
    print("confused")
    dictOfPDs={}
    #print(dictOfPDs['KC328452'])
    number=1    
    uniquePDNumbers=list(dfPDs['CCPO ID'])   
    print("got here")
    currenttime=datetime.now().strftime("%m%d%Y %H%M%S")
    #initialDF.to_excel(f"archive DF {currenttime}.xlsx")
    initialDF.to_pickle(f"archive DF {currenttime}.pkl")
    initialDF.to_csv(f"archive DF {currenttime}.csv")
    undonePDNumbers=list(set(uniquePDNumbers) - set(list(initialDF['CCPO ID'])))
    print(undonePDNumbers)
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
        if number%100==0:
            print(number)
            writeOut(dictOfPDs)  
    return(dictOfPDs)
        
def runAll():    
    try:
        dfPDs=pd.read_excel("exportIDs.xlsx")
    except:
        df=readData('CP DATA 22SEP2021.xlsx') 
        df=genID(df)
        dfPDs=pd.read_excel("exportIDs.xlsx")
    try: 
        initialDF=pd.read_excel("textScapePD.xlsx")
        print("did inital")
    except:
        initialDF=pd.DataFrame()
    PDText=getPDLookups(dfPDs, initialDF)
    print(len(PDText))
    PDText=writeOut(PDText)
    print(len(PDText))
    return(PDText)
    
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
            print(topResult)
            text=scrapePD(topResult)
            dictText[term]=text
        except:
            dictText[term]=term
            print(term)
    listForDF = list(zip(dictText.keys(), dictText.values()))
    PDTextFailed = pd.DataFrame(listForDF, columns = ['CCPO ID', 'PD Text'])
    return(PDTextFailed)
        

def cleanBlankStragglers(fileName):
    df=pd.read_excel(fileName)
    
    failedLinks=list(df.loc[df["PD Text"].astype(str).str.contains("search_fs_output")]['PD Text'])
    cleanerFailedLinks=["ht"+i.split("ht")[1].split("%3D")[0]+"%3D" for i in failedLinks]
    #ok so that one worked
    PDTextFailed=cleanFailedLinks(cleanerFailedLinks)
    
    blanksCCPs= pd.Series(list(df.loc[df["PD Text"].astype(str).str.contains("search_fs_output")]['CCPO ID']))
    
    PDTextFailed['CCPO ID']= blanksCCPs
    keepdf=df.loc[~df['PD Text'].isin(failedLinks)]
    fixedBlank=pd.concat([keepdf[['CCPO ID', 'PD Text']],PDTextFailed])
    fixedBlank['Length']=fixedBlank['PD Text'].astype(str).str.len()
    noLinks=list(fixedBlank.loc[fixedBlank["Length"]<1000]['CCPO ID'])
    PDTextLinkFailed=cleanNoLinks(noLinks)
    PDTextLinkWorked=PDTextLinkFailed.loc[PDTextLinkFailed['Length']>100][['CCPO ID', 'PD Text']]
    fixedBlank=fixedBlank.loc[~fixedBlank['CCPO ID'].isin(list(PDTextLinkWorked['CCPO ID']))]
    fixedMissingBlank=pd.concat([fixedBlank,PDTextLinkWorked])
    return(fixedMissingBlank)
    #I have 137 with nothing


def cleanText(string):
    try:
        cleanStart="PD#"+ string.split("PD#", maxsplit=1)[1]
        delChars=["xa0","'", "\\","}", "{", "}" ]
        for char in delChars:
            cleanStart=cleanStart.replace(char,"")
        #ideally we do this in a dictionary but that seems like the least of the issues
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
        
PDText=runAll()
#fixedMissingBlank=cleanBlankStragglers("textScapePDx.xlsx")


#fixedMissingBlank['cleanText']=fixedMissingBlank['PD Text'].apply(cleanText)

#dfPeople=readData('CP DATA 22SEP2021.xlsx') 
#dfPeople['CCPO ID']=dfPeople['Ccpo Id']+dfPeople['CPCN']   
#merged=dfPeople.merge(df, left_on='CCPO ID', right_on='CCPO ID')

#hasCP36=merged.loc[merged['cleanText'].astype(str).str.contains("CP:36")]

