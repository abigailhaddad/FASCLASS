# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 11:15:13 2021
compare FM PD data with FM reports
@author: HaddadAE
"""

import pandas as pd
import os
import numpy as np
from win32com.client import Dispatch
from datetime import date



os.chdir(os.getcwd().replace("code", "data"))
os.chdir('reports')

def readInDFs():
    dfs = {}
    for i in os.listdir():
        name=i.split(".")[0]
        try:
            file = pd.read_excel(i)
        except:
            file = pd.read_csv(i)
        file['fileName']=name
        dfs[name]=file
    return(dfs)

def processVantage(dfs):
    vantagePeople=dfs['people with FM PD from Vantage']
    vantagePeople['Name_Pers']=vantagePeople['Name_Pers'].str.upper().str.replace(",","").str.replace(".","").str.strip()
    vantagePeople=vantagePeople.rename(columns={"PD": "PD_Vantage"})
    return(vantagePeople)
    
def processReport(dfs, fileName):
    enrolledPeople=dfs[fileName].drop_duplicates()
    enrolledPeople['Employee']=enrolledPeople['Employee'].str.upper().str.replace(",","").str.replace(".","").str.strip()
    enrolledPeople=enrolledPeople.rename(columns={"PD": "PD_Report"})
    try:
        enrolledPeople=enrolledPeople.loc[enrolledPeople['Pos Code']!="FMC0"]
    except:
        enrolledPeople['Pos Code']="None"
    return(enrolledPeople)
    
def matchBoth(vantagePeople, enrolledPeople):
    ### First group: people who match on NAME and PD
    matchOnBoth=vantagePeople.merge(enrolledPeople, left_on=['Name_Pers', 'PD_Vantage'],
                                right_on=['Employee', 'PD_Report'], how='outer', 
                                indicator=True)
    matched=matchOnBoth.loc[matchOnBoth["_merge"]=="both"]
    matched['Match Type']="Matched on Both Name and PD"
    matched=matched.drop(columns=['_merge'])
    justVantage=matchOnBoth.loc[matchOnBoth["_merge"]=="left_only"]
    justVantage=justVantage.drop(columns=['_merge'])
    justVantage=justVantage.dropna(how='all', axis=1)
    justVantage['Match Type']="Just in Vantage"
    justReport=matchOnBoth.loc[matchOnBoth["_merge"]=="right_only"]
    return(matched, justVantage, justReport)
    
def genMatchOnName(justVantage, justReport):
    justReport=justReport.drop(columns=['_merge'])
    justReport=justReport.dropna(how='all', axis=1)
    matchOnName=justVantage.merge(justReport, left_on=['Name_Pers'],
                                right_on=['Employee'], how='outer', 
                                indicator=True)
    matchedName=matchOnName.loc[matchOnName["_merge"]=="both"]
    matchedName['Match Type']="Matched on Name"
    matchedName=matchedName.drop(columns=['_merge'])
    justVantage=matchOnName.loc[matchOnName["_merge"]=="left_only"]
    return(matchOnName, matchedName, justVantage)

def mergePD(matchOnName, justReport, justVantage, vantagePeople):
    justVantage=justVantage.drop(columns=['_merge'])
    justVantage=justVantage.dropna(how='all', axis=1)
    justReport=matchOnName.loc[matchOnName["_merge"]=="right_only"]
    justReport=justReport.drop(columns=['_merge'])
    justReport=justReport.dropna(how='all', axis=1)
    allPDs=vantagePeople[['CCPO_ID_2', 'FM_Cert', 'FM_Cert_Removed', 'Level_1', 'Level_2',
       'Level_3',  'CareerProgram', 'PD_Text', 'PD_Vantage',
       'Total']].drop_duplicates()
    matchOnPD=justReport.merge(allPDs, left_on=['PD_Report'],
                                right_on=['PD_Vantage'], how='left', 
                                indicator=True) 
    return(justVantage, justReport, matchOnPD)

def cleanPeople(matched, matchedName, matchOnPD, justVantage, fileName):
    matchOnPD['Match Type']=np.where(matchOnPD['_merge']=="left_only", f"Just in {fileName} Report", "Matched on PD")
    matchOnPD=matchOnPD.drop(columns=['_merge'])
    allPeople=pd.concat([matched, matchedName, matchOnPD, justVantage])
    allPeople=allPeople.drop(columns=['fileName_y', 'fileName_x'])
    allPeople['Match Code']="No Match/Unclear"
    a=(allPeople['Pos Code']=="FMC02")
    b=(allPeople['Level_2']==1)
    allPeople['Match Code']=np.where((a & b), "Match", allPeople['Match Code'])
    c=(allPeople['Pos Code']=="FMC03")
    d=(allPeople['Level_3']==1)
    allPeople['Match Code']=np.where((c & d), "Match", allPeople['Match Code'])
    e=(allPeople['Pos Code']=="FMC01")
    f=(allPeople['Level_1']==1)
    allPeople['Match Code']=np.where((e & f), "Match", allPeople['Match Code'])
    return(allPeople)
    
def cleanfirstLastcomma(string):
    try:
        if string[0]==",":
            string=string[1:]
        if string[-1]==",":
            string=string[0:-1]
    except:
        pass
    return(string)
    
def concatTextSet(df, unique):
    colList=list(df.columns)
    colList.remove(unique)
    indexDF=pd.DataFrame(index=df[unique].unique())
    for col in colList:
        df[col]=df[col].astype(str)
        df[col]=df[col].str.replace("nan","")
        grouped=df.groupby([unique])[col].apply(set).apply(','.join)
        indexDF=indexDF.merge(grouped, left_index=True, right_index=True)
        indexDF[col]=indexDF[col].apply(cleanfirstLastcomma)
    return(indexDF)
    

def allTheThings(dfs, fileName):
    vantagePeople=processVantage(dfs)
    enrolledPeople=processReport(dfs, fileName)
    matched, justVantage, justReport= matchBoth(vantagePeople, enrolledPeople)
    matchOnName, matchedName, justVantage=genMatchOnName(justVantage, justReport)
    justVantage, justReport, matchOnPD=mergePD(matchOnName, justReport, justVantage, vantagePeople)
    allPeople=cleanPeople(matched, matchedName, matchOnPD, justVantage, fileName)
    return(allPeople)
    
def getAllData():
    dfs=readInDFs()
    fileName='CP11EnrolledNov1021'
    allPeopleEnrolled=allTheThings(dfs, fileName)
    allPeopleEnrolled=allPeopleEnrolled.rename(columns={'Match Type': 'Match Type with Enrolled', 'Match Code': "Match Code With Enrolled"})
    fileName='CP11NotEnrolledNov1021'
    allPeopleNotEnrolled=allTheThings(dfs, fileName)
    allPeopleNotEnrolled.loc[allPeopleNotEnrolled['Match Type']!="Just in Vantage"]
    allPeopleNotEnrolled=allPeopleNotEnrolled.rename(columns={'Match Type': 'Match Type with Not Enrolled',
                                                    'Match Code': "Match Code With Not Enrolled"})

    allPeople=pd.concat([allPeopleNotEnrolled, allPeopleEnrolled])

    indexDF=concatTextSet(allPeople, 'Employee')
    return(indexDF)


def summarizeStatus(indexDF):
    indexDF['Summary of Match Status']="Unknown"
    a=indexDF['Match Type with Enrolled']=="Matched on Both Name and PD"
    b=indexDF['Match Type with Not Enrolled']==""
    c=indexDF["Match Code With Enrolled"]=="Match"
    indexDF['Summary of Match Status']=np.where((a & b & c), "Enrolled, Matched Correctly", indexDF['Summary of Match Status'])

    d=indexDF['Match Type with Enrolled']==""
    e=indexDF['Match Type with Not Enrolled']=="Just in CP11NotEnrolledNov1021 Report"
    indexDF['Summary of Match Status']=np.where((d & e), "Not Enrolled, Matched Correctly", indexDF['Summary of Match Status'])

    f=indexDF['Match Type with Not Enrolled']=="Matched on Both Name and PD"
    indexDF['Summary of Match Status']=np.where((d & f), "Not Enrolled, Should Be", indexDF['Summary of Match Status'])

    g=indexDF['Match Type with Enrolled']=="Just in CP11EnrolledNov1021 Report"
    indexDF['Summary of Match Status']=np.where((b & g), "Enrolled, Should Not Be", indexDF['Summary of Match Status'])
    
    indexDF['Summary of Match Status']=np.where((a & b & ~c), "Enrolled, Matched Not Correctly", indexDF['Summary of Match Status'])
    
    indexDF['Summary of Match Status']=np.where((~b & a & c), "Enrolled and Not Enrolled, Matched Correctly", indexDF['Summary of Match Status'])
    indexDF['Summary of Match Status']=np.where((~b & a & ~c), "Enrolled and Not Enrolled, Not Matched Correctly", indexDF['Summary of Match Status'])
    
    return(indexDF)

def mapColors():
    colorDict={'Not Enrolled, Should Be': "#F7D17A" ,
               'Enrolled and Not Enrolled, Matched Correctly': "#CCFFCC",
               'Enrolled and Not Enrolled, Not Matched Correctly': "#E8B3A6",
               'Unknown': "#F1F5CC",
               'Not Enrolled, Matched Correctly': "#A0F77A" ,
               'Enrolled, Matched Correctly': "#99CC00",
               'Enrolled, Matched Not Correctly':"#F7EACF" ,
               'Enrolled, Should Not Be': "#F7CFF3"}
    return(colorDict)

def highlight_cells(series):
    value=series['Summary of Match Status']
    color="#FFFFFF"
    colorDict=mapColors()
    for key in list(colorDict.keys()):
        if value==key:
            color=colorDict[key]
            
    return [f"background-color: {color}"] * len(series)


def cleanUpRawData(df):
    for col in ['Level_1', 'Level_2', 'Level_3', 'FM_Cert_Removed', 'FM_Cert', 'Total']:
        df[col]=df[col].str.replace(".0", "")
    df['Cert End Date']=df['Cert End Date'].str.replace("NaT","")
    return(df)
    
def autoFit(fileName):
    excel = Dispatch('Excel.Application')
    wb = excel.Workbooks.Open(fileName)
    #Activate second sheet
    for i in range(1,4):
        excel.Worksheets(i).Activate()
        #Autofit column in active sheet
        excel.ActiveSheet.Columns.AutoFit()
    wb.SaveAs(fileName)
    wb.Close()


indexDF=getAllData()
indexDF=cleanUpRawData(indexDF)
indexDF=summarizeStatus(indexDF)
summary=indexDF['Summary of Match Status'].value_counts().to_frame().reset_index()
summary=summary.rename(columns={"Summary of Match Status": "Count",
                                   "index": "Summary of Match Status"})
summary['Count']=summary['Count'].astype(float)
summary.style.format=summary.style.format({'Count': "{:,.0f}"})
fileName="FM Reports and PD Analysis Summary.xlsx"
writer = pd.ExcelWriter(fileName, engine="xlsxwriter")

author="Abigail Haddad"
files='CP11EnrolledNov1021, CP11NotEnrolledNov1021, PD Analysis'
today= date.today().strftime("%B %d, %Y")


df=pd.DataFrame(index=["Date", "Files", "Author"], columns=["Values"], data=[today, files, author])


df2 = summary.style.apply(highlight_cells, axis=1)
df2.to_excel(writer, index=False, sheet_name="Summary")

df3 = indexDF.style.apply(highlight_cells, axis=1)
df3.to_excel(writer, index=False, sheet_name="Raw Data")
writer.save()


autoFit(fileName)




#Save changes in a new file


#Or simply save changes in a current file
#wb.Save()

