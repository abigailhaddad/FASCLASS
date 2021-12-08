# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 10:00:01 2021
this is for processing the reports given to me to reconcile them with FASCLASS results
@author: HaddadAE
"""

import pandas as pd
import os

os.chdir(os.getcwd().replace("code", "data"))
os.chdir('reports')

def readInDFs():
    dfs = {}
    for i in os.listdir():
        name=i.split(".")[0]
        file = pd.read_excel(i)
        file['fileName']=name
        dfs[name]=file
    return(dfs)
    
def findDupNames(dfs):
    allCP11=pd.concat([dfs['CP11EnrolledNov1021'].drop_duplicates(), dfs['CP11NotEnrolledNov1021'].drop_duplicates()])
    counts=allCP11['Employee'].value_counts().reset_index()
    counts.columns=['Employee', 'Count']
    allCP11WithCount=allCP11.merge(counts, left_on='Employee', right_on='Employee')
    employeeFile=allCP11[['Employee', 'fileName']].drop_duplicates()
    employeeFileGroup=employeeFile.groupby(['Employee'])['fileName'].apply(','.join).reset_index()
    employeeFileGroup.columns=['Employee', 'allFileNameByPerson']
    finalEmployee=allCP11WithCount.merge(employeeFileGroup, left_on='Employee', right_on='Employee')
    return(finalEmployee)
    
    
def fixDataErrors(dfs):
    enrolledNames=list(set(dfs['CP11EnrolledNov1021']['Employee']))
    nonEnrolled=dfs['CP11NotEnrolledNov1021'].loc[~dfs['CP11NotEnrolledNov1021']['Employee'].isin(enrolledNames)].drop_duplicates()
    enrolled=dfs['CP11EnrolledNov1021'].drop(columns=['Cert End Date']).drop_duplicates().sort_values('Status')
    #if there is a status of completed for an employee-pers code combo, drop any other lines
    #let's just get the completeds, and then we're gonna do a left join to the noncompleteds
    mergeFields=['Employee', 'Pos Code', 'Per Code']
    complete=enrolled.loc[enrolled['Status']=="COMPLETED"]
    noncomplete=enrolled.loc[enrolled['Status']!="COMPLETED"]
    merges=noncomplete.merge(complete[mergeFields], left_on=mergeFields, right_on=mergeFields, how='left', indicator=True)
    nodupes=merges.loc[merges["_merge"]=="left_only"].drop(columns=['_merge'])
    droppedDupes=pd.concat([nodupes, complete, nonEnrolled]).drop_duplicates()
    #we're going to keep the non-merges
    positionPeople=droppedDupes.drop(columns=['Per Code']).drop_duplicates()
    positionPeople['Pos Code']=positionPeople['Pos Code'].fillna("None")
    positionPeople=positionPeople.sort_values('Pos Code')
    tailed=positionPeople.sort_values('Pos Code').groupby('Employee').tail(1)
    
    #and then append them to the completeds
    
def getJustPosCode(dfs):
    #this code shows what we have people as coded for in their positon
    enrolledNames=list(set(dfs['CP11EnrolledNov1021']['Employee']))
    nonEnrolled=dfs['CP11NotEnrolledNov1021'].loc[~dfs['CP11NotEnrolledNov1021']['Employee'].isin(enrolledNames)].drop_duplicates()
    enrolledDrop=['Per Code', 'Status', 'Cert End Date']
    enrolledNoDupes=dfs['CP11EnrolledNov1021'].drop(columns=enrolledDrop).drop_duplicates()
    tailed=enrolledNoDupes.groupby(['Employee', 'Pos Code']).tail(1)
    enrolledAndNot=pd.concat([tailed,nonEnrolled])
    return(enrolledAndNot)


def mergeInTemp(dfs, enrolledAndNot):
    #we want to get all the people from 'TempsorTermsWithFMCNov1021' who are not in enrolledAndNot
    #and we want to get work schedule and appointment for people who are in both
    namesInenrolledandnot=list(enrolledAndNot['Employee'])
    onlyInTempsorTerms=dfs['TempsorTermsWithFMCNov1021'].loc[~dfs['TempsorTermsWithFMCNov1021']['Employee'].isin(namesInenrolledandnot)]
    
    formergein=dfs['TempsorTermsWithFMCNov1021'].loc[dfs['TempsorTermsWithFMCNov1021']['Employee'].isin(namesInenrolledandnot)][['Employee', 'PD', 'Work Schedule',
       'Appointment']]
    final=enrolledAndNot.merge(formergein, left_on=['Employee', 'PD', 'Work Schedule', 'Appointment'], right_on=['Employee', 'PD', 'Work Schedule', 'Appointment'], how="outer", indicator=True)
    if final['_merge'].value_counts()['right_only']>0:
        print("something broke y'all")
    else:
        final=final.drop(columns=['_merge'])
    
    inTempTermAll=pd.concat([final, onlyInTempsorTerms]).drop(columns=['CP',
       'Per Code', 'Status', 'Cert End Date'])
    inTempTermAll['Employee']=inTempTermAll['Employee'].str.replace(",","").str.replace(".","").str.strip()
    return(inTempTermAll)

def defineIntersection(series1, series2):
    overlap=[i for i in series1 if i in series2]
    print(f'overlap is {len(overlap)}')
    print(f'examples are {overlap[0:5]}' )
    print()
    leftonly=[i for i in series1 if i not in series2]
    print(f'left only is {len(leftonly)}')
    print(f'examples are {leftonly[0:5]}' )
    print()
    rightonly=[i for i in series2 if i not in series1]
    print(f'right only is {len(rightonly)}')
    print(f'examples are {rightonly[0:5]}' )       
    return(overlap, leftonly, rightonly)
    
dfs=readInDFs()
#allCP11WithCount=findDupNames(dfs)
#allCP11WithCount.to_excel("CP 11 With Name Count.xlsx")
enrolledAndNot=getJustPosCode(dfs)
enrolledPlusTemp= mergeInTemp(dfs, enrolledAndNot)


def mergeInUserData(dfs, enrolledPlusTemp):
    df=dfs['FM09 CIV DATA USER REPORT']
    df=df.loc[df['Employee Type']=="CIV"]
    df['Employee']=df['User Name'].str.upper().str.replace(",","").str.replace(".","").str.strip()
    allData=df.merge(enrolledPlusTemp, left_on=['Employee'], right_on=['Employee'], how='outer', indicator=True)
    return(allData)

    

allData=mergeInUserData(dfs, enrolledPlusTemp)

civsInOther=list(enrolledPlusTemp['Employee'])
civsInDf=list(dfs['FM09 CIV DATA USER REPORT'].loc[dfs['FM09 CIV DATA USER REPORT']['Employee Type']=="CIV"]['Employee'])

overlap, leftonly, rightonly=defineIntersection(civsInOther, civsInDf)
    
### ANSWER THE FUCKING QUESTIONS AND STOP CODING
## document inconsistencies within your data
#first of all, we have people in both 'CP11EnrolledNov1021' and 'CP11NotEnrolledNov1021'
#we're ignoring if they're in not enrolled 
df=dfs['FM09 CIV DATA USER REPORT']
civ=df.loc[df['Employee Type']=="CIV"]['User Name'].str.upper().str.replace(",","").str.replace(".","").str.strip()
mil=df.loc[df['Employee Type']=="MIL"]['User Name'].str.upper().str.replace(",","").str.replace(".","").str.strip()

overlap, leftonly, rightonly=defineIntersection(civsInOther, mil)
df=df.loc[df['Employee Type']=="CIV"]
df['derived type']=df['Email Address'].str.split("@").str[0].str.split(".").str[-1]

"""
I'm trying to figure out some details on the 'CP11EnrolledNov1021' and 'CP11NotEnrolledNov1021' files. First,
there were a lot of pure duplicates, but I just deleted those. Second, I see some employees with a line that says "PENDING" and another line
that says "COMPLETED" for the same certification - that is, with the same "Per Code" value. I assume in those cases I should just assume
that the "PENDING" one is out of date? Bigger issue, though: there's a lot of overlap between these two data sets,
with about 4,000 employee names appearing in both. How should I interpret that?



tempEmp=list(dfs['TempsorTermsWithFMCNov1021']['Employee'])



countByEmp=allCP11['Employee'].value_counts()
morethanone=list(countByEmp.loc[countByEmp>1].index)
morethanonefull=allCP11.loc[allCP11['Employee'].isin(morethanone)]

countPTname=morethanonefull.groupby(['Employee', 'Position Title']).count()['fileName'].reset_index()
"""

name="JACKSON JOAN R"
for df in dfs.values():
    for col in ['Employee', 'User Name']:
        try:            
            subset=df.loc[df[col].str.upper().str.replace(",","").str.replace(".","")==name]
            if len(subset)>0:
                print(df['fileName'].unique())
                print(subset.iloc[0])
        except:
            pass
