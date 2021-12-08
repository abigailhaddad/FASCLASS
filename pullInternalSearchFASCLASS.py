# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:43:37 2021

@author: HaddadAE
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
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
    
def genDriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    return(driver)
    
def test_search(undonePDNumbers):
    urls=[]
    driver=genDriver()
    driver.get("https://acpol2.army.mil/fasclass/search_fs/search_fasclass.asp")
    driver.switch_to.alert.accept()
    driver.set_window_size(1050, 708)
    # Test name: search
    # Step # | name | target | value
    # 1 | open | /fasclass/search_fs/search_fasclass.asp | 
    for PDnumber in undonePDNumbers:
        CCPOKeys=PDnumber[0:2]
        JobNumKeys=PDnumber[2:]        
        # 2 | setWindowSize | 1050x708 |  
        # 3 | type | name=Ccpo | ER
        driver.find_element(By.NAME, "Ccpo").send_keys(CCPOKeys)
        # 4 | click | name=JobNum | 
        driver.find_element(By.NAME, "JobNum").click()
        # 5 | type | name=JobNum | 544175
        driver.find_element(By.NAME, "JobNum").send_keys(JobNumKeys)
        # 6 | click | name=submit1 | 
        driver.find_element(By.NAME, "submit1").click()
        # 7 | click | linkText=ER544175 | 
        try:
            driver.find_element(By.LINK_TEXT, PDnumber).click()
            url=driver.current_url
            urls.append((url+"%3D")[:-3])
        except:
            url=("no link")
            urls.append(url)
        driver.get("https://acpol2.army.mil/fasclass/search_fs/search_fasclass.asp")
        print(PDnumber)
    driver.quit()
    return(urls)
        
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
    undonePDNumbers=list(dfPDs['CCPO ID'])
    listOfLinks=test_search(undonePDNumbers)
    for number in range(0, len(undonePDNumbers)):
        PDnumber=undonePDNumbers[number]
        link=listOfLinks[number]
        try:
            dictOfPDs[PDnumber ]=scrapePD(link, PDnumber)
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
           
def makeDF(PDText):
    listForDF = list(zip(PDText.keys(), PDText.values()))
    PDText = pd.DataFrame(listForDF, columns = ['CCPO ID', 'PD Text'])
    return(PDText)
    
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
    df['PD Text']=df['PD Text'].apply(cleanText)
    writeOut(df)

def runAll():    
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
                            
def getPD(text):
    try:
        PD=text.split("PD#:", 1)[1].split("Sequence#", 1)[0].strip()
        return(PD)
    except:
        return()
        
runAll()