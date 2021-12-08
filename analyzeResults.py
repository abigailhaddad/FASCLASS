# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 12:51:59 2021

@author: HaddadAE
"""

import os
import pandas as pd
os.chdir(os.getcwd().replace("code", "data"))
import re

def readData(fileName):
    # you need to specify the engine depending on the versions of the libraries
    df=pd.read_excel(fileName, engine='openpyxl')
    return(df)
"""


    
df=readData('CP DATA 22SEP2021.xlsx')

for i in df.columns:
    print(i)
    print(len(df[i].unique()))
    print(len(df[i].unique())/len(df))
    print()
    
comptroller=df.loc[df['Ar Psn Car Pgm Cd description'].str.contains("COMPTROLLER")]

for i in comptroller.columns:
    print(i)
    print("all")
    print(df[i].value_counts(normalize=True).head())
    print("11")
    print(comptroller[i].value_counts(normalize=True).head())
    print()
    
    #merged['careerCat']=merged['PD Text'].apply(findCareerCategory)

def careerFields():

    listOfCareerFields=["ENGINEERING","LIFE CYCLE LOGISTICS", "CONTRACTING", "FACILITIES ENGINEERING",
                    "PROGRAM MANAGEMENT", "INFORMATION TECHNOLOGY",  "BUSINESS - FINANCIAL MGMT", 
                    "TEST AND EVALUATION", "PRODUCTION, QUALITY AND MANUFACTURING",
                    "SCIENCE AND TECHNOLOGY MANAGER", "BUSINESS - COST ESTIMATING",
                    "PURCHASING", "PROGRAM MANAGEMENT SPECIALIST", "SENIOR CONTRACTING OFFICIAL",
                    "CATEGORY NOT IDENTIFIABLE" ,"INDUSTRIAL/CONTRACT PROPERTY MGMT", "CONFIGURATION/DATA MANAGEMENT",
                    "SCIENTIST"]
    return(listOfCareerFields)
    
def findFromList(string):
    output=""
    toFind=careerFields()
    for substring in toFind:
        if substring in string:
            output=output+", "+ substring
    return(output)
    
merged['careerList']=merged['PD Text'].apply(findFromList)

def findCareerCategory(string):
    listNext=string.split("Career Category")
    lastOne=listNext[-1][0:50]
    capitols=[i for i in lastOne if i.upper()==i]
    joined=("".join(capitols))
    split=joined.split("C L")[0]
    return(split.replace(":","").strip())



#df=pd.read_csv('aggregatePD.csv')
dfPeople=readData('CP DATA 22SEP2021.xlsx') 
dfPeople['CCPO ID']=dfPeople['Ccpo Id']+dfPeople['CPCN']
#merged=dfPeople.merge(df, left_on='CCPO ID', right_on='CCPO ID')

toDrop=['Name Pers', 'DOD ID (EDIPI)', 'SCD Civ', 'Dt Start Pres Posn']

for i in dfPeople.columns:
    print(i)
    print(len(dfPeople[i].unique())/len(dfPeople))
    print()

hasCP36=merged.loc[merged['PD Text'].astype(str).str.contains("CP:36")]



    
def findCarCat(string):
    try:
        afterSub=string.split("Career Category:")[1]
        beforeNext=afterSub.split("Career Level:")[0]
        return(beforeNext.strip())
    except:
        return("BLANK")
        
def findCareerProgram(string):
    try:
        listNext=string.lower().split("career program")
        split=listNext[-1][0:60].replace(":", "").strip().split("  ")
        lastOne=split[0]
        numeric_string = re.sub("[^0-9%]", "", lastOne)
        firstNum=numeric_string.split()[0]
        if len(firstNum)==2:
            return(firstNum)
    except:
        return("")
        
    

merged['CP']=merged['PD Text'].apply(findCP)
merged['careerCat']=merged['PD Text'].apply(findCarCat)
merged['career pr']=merged['PD Text'].apply(findCareerProgram)


for item in merged['careerCat'].unique():
    subset=merged.loc[merged['careerCat']==item]
    print([item+ "  " ]*3)
    print(subset['Ar Psn Car Pgm Cd description'].value_counts().head(10))
    print()
    
comptroller=merged.loc[merged['Ar Psn Car Pgm Cd description']=="COMPTROLLER"]
comptroller['careerCat'].value_counts()

comptroller['CP'].value_counts()
comptroller['career pr'].value_counts()


allValues=merged['career pr'].unique()
missings=[i for i in allValues if str(i) not in list(merged['Ar Psn Car Pgm Cd'].astype(str).unique())]

fileName="textScrape 10072021 035854.xlsx"
df=pd.read_excel(fileName)
text=df.iloc[5]['PD Text']

text.replace("\xa0","")

text=text.replace("\xa0","")

PD=text.split("PD#:", 1)[1].split("Sequence#", 1)[0].strip()
sequence=text.split("Sequence#:")[1].split("Replaces PD", 1)[0].strip()
                    
def getPD(text):
    try:
        PD=text.split("PD#:", 1)[1].split("Sequence#", 1)[0].strip()
        return(PD)
    except:
        return()
        
def getSequence(text):
    try:
        sequence=text.split("Sequence#:")[1].split("Replaces PD", 1)[0].strip()
        return(sequence)
    except:
        return()
        
def getReplaces(text):
    try:
        unclean=text.split("Replaces PD#: ")[1].split("Organization Title",1)[0]
        replaces=" ".join(unclean.strip().split()[:-1])
        return(replaces)
    except:
        return()
        
def getOrgTitle(text):
    #this field is empty
    try:
        title=text.split("Organization Title:", 1)[1].split("POSITION LOCATION:", 1)[0].strip()
        return(title)
    except:
        return()

def reviewDataClassification(text):
    try:
        unclean=text.split("Reviewed By:")[1].split("Reviewed Date:",1)[1]
        date=unclean.split("POSITION INFORMATION")[0].strip()
        return(date)
    except:
        return()
    
def positionDuties(text):
    try:
        position=text.split("POSITION DUTIES:")[1].split("Fair Labor Standards Act", 1)[0].strip()
        return(position)
    except:
        return()
        
df['PD']=df['PD Text'].apply(getPD)
df['Sequence']=df['PD Text'].apply(getSequence)
df['Replaces']=df['PD Text'].apply(getReplaces)
df['Organization Title']=df['PD Text'].apply(getOrgTitle)
df['Date of Classification Review']=df['PD Text'].apply(reviewDataClassification)
df['Year of Classification Review']=df['Date of Classification Review'].str[-4:]
df['Position Text']=df['PD Text'].apply(positionDuties)
 
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


def findCP(string):
    listNext=string.split("CP")
    lastOne="CP"+listNext[-1][0:10]
    return(lastOne)

df=readData('CP DATA 22SEP2021.xlsx')
pds=pd.read_csv("aggregatePD.csv", engine='python')
df['CCPO ID']=df['Ccpo Id']+df['CPCN']
df['Name Pers']=df['Name Pers'].str.replace("TRAN,,", "TRAN,")
merged=df.merge(pds, left_on='CCPO ID', right_on='CCPO ID', how='left')
merged.count()

"""

aList=['CCPO_ID', 'PD_Text', 'CCPO_ID_2', 'untitled_column', 'PD', 'Sequence', 'ReplacesPD', 'OrganizationTitle', 'POSITIONLOCATION', 'ServicingCPAC', 'Agency', 'Installation', 'ArmyCommand', 'Region', 'CommandCode', 'POSITIONCLASSIFICATIONSTANDARDSUSEDINCLASSIFYINGGRADINGPOSITION', 'SupervisoryCertification', 'SupervisorName', 'ReviewedDate', 'ClassificationReview', 'ReviewedBy', 'ReviewedDate_2', 'POSITIONDUTIES', 'FairLaborStandardsActFLSADetermination', 'FLSACommentsExplanations', 'CyberWorkforce', 'PrimaryWorkRole', 'AdditionalWorkRole1', 'AdditionalWorkRole2', 'FLSA', 'FLSAWorksheet', 'FLSAAppeal', 'BusCode', 'MissionCategory', 'WorkCategory', 'WorkLevel', 'AcquisitionPosition', 'CAP', 'CareerCategory', 'CareerLevel', 'FunctionalCode', 'Interdisciplinary', 'SupervisorStatus', 'PDStatus', 'CONDITIONOFEMPLOYMENT', 'DrugTestRequired', 'FinancialManagementCertification', 'PositionDesignation', 'PositionSensitivity', 'SecurityAccess', 'EmergencyEssential', 'RequiresAccesstoFirearms', 'PersonnelReliabilityPosition', 'InformationAssurance', 'InfluenzaVaccination', 'FinancialDisclosure', 'FinancialDisclosure_2', 'EnterprisePosition', 'POSITIONASSIGNMENT', 'CompetitiveArea', 'CompetitiveLevel', 'CareerProgram', 'CareerLadderPD', 'TargetGradeFPL', 'CareerPos1', 'CareerPos2', 'CareerPos3', 'CareerPos4', 'CareerPos5', 'Title', 'PayType']
len(a)