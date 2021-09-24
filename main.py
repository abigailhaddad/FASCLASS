# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 09:20:19 2021

@author: HaddadAE
"""

import os
import pandas as pd
#from googlesearch import search
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

os.chdir(os.getcwd().replace("code", "data"))

def readData(fileName):
    df=pd.read_excel(fileName)
    return(df)
    
def genID(df):
    df['CCPO ID']=df['Ccpo Id']+df['CPCN']
    df[['CCPO ID']].drop_duplicates().to_excel("exportIDs.xlsx")
    return(df)


    
def getLinks(term):
    links=[]
    headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
            }
    page = requests.get("https://www.bing.com/search?", headers=headers, params={"q": term}).text
    soup = BeautifulSoup(page, 'html.parser')

    anchors = soup.find_all("a")
    for anchor in anchors:
        if anchor is not None:
            try:
                if "http" in anchor["href"]:
                    links.append((anchor.getText(), anchor["href"])[1])
            except KeyError:
                continue     

    return(links)
    
    
def getRightLink(PDnumber):
    links=getLinks(PDnumber)
    findStr="search_fs_output"
    topResult=[j for j in links if findStr in j][0]
    return(topResult)
    
def scrapePD(link):
    page = urlopen(link)
    html_bytes = page.read()
    soup = BeautifulSoup(html_bytes, 'html.parser')
    text=soup.get_text().replace("\n","").replace("\t","").replace("\r","").replace("\xa0","").split("POSITION DESCRIPTION")[1]
    print("worked")
    return(text)
    return()
    
def getPDLookups(dfPDs):
    #uniquePDNumbers=df['CCPO ID'].value_counts().index
    uniquePDNumbers=list(dfPDs['CCPO ID'])
    
    dictOfPDs={}
    for PDnumber in uniquePDNumbers[0:5]:
        try:
            link=getRightLink(PDnumber)
        except:
            link=""
        try:
            dictOfPDs[PDnumber]=scrapePD(link)
        except:
            dictOfPDs[PDnumber]=link
    return(dictOfPDs)
    
def runAll():    
    try:
        dfPDs=pd.read_excel("exportIDs.xlsx")
    except:
        df=readData('CP DATA 22SEP2021.xlsx') 
        df=genID(df)
        dfPDs=pd.read_excel("exportIDs.xlsx")
    PDText=getPDLookups(dfPDs)
    listForDF = list(zip(PDText.keys(), PDText.values()))
    PDText = pd.DataFrame(listForDF, columns = ['CCPO ID', 'PD Text'])
    PDText .to_excel("textScapePD.xlsx")
    return(PDText )
        
    
    
PDText=runAll()


"""

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re

req = Request("https://acpol2.army.mil/fasclass/search_fs/search_fasclass_result.asp?fcp=zutpk3eFRsFxhouYmqtGvqy2heWSqYuts7NklA%3D%3D")
html_page = urlopen(req)

soup = BeautifulSoup(html_page, "lxml")

links = []
for link in soup.findAll('a'):
    links.append(link.get('href'))

print(links)
"""
