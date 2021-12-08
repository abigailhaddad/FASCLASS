# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 11:58:54 2021

@author: HaddadAE
"""
import pandas as pd
import re
import os

os.chdir(os.getcwd().replace("code", "data"))

def decode(text):
    encoded_string = text.encode("ascii", "ignore")
    decode_string = encoded_string.decode()
    return(decode_string)
    
def getSection(text, string1, string2):
    try:
        toreturn1=text.split(string1, 1)[1]
        toreturn2=toreturn1.split(string2, 1)[0].strip()
        return(toreturn1, toreturn2)
    except:
        pass
    
def getRealCleanPDs():
    pds=pd.read_csv("aggregatePD.csv", engine='python')
    realPDs=pds.loc[pds['PD Text'].notnull()]
    realPDs=realPDs.loc[realPDs['PD Text']!="()"]
    realPDs['PD Text']=realPDs['PD Text'].astype(str).apply(decode)
    return(realPDs)
    
def genPieces():
    listOfPieces=["PD#:", "Sequence#:", "Replaces PD#:", "Organization Title:", "POSITION LOCATION:", 
              "Servicing CPAC:", "Agency:", "Installation:", "Army Command:", 
              "Region:", "Command Code:","POSITION CLASSIFICATION STANDARDS USED IN CLASSIFYING/GRADING POSITION:",
              "Supervisory Certification:", "Supervisor Name:",
              "Reviewed Date:", "Classification Review:","Reviewed By:",
              "Reviewed Date:", "POSITION INFORMATION :", 
              "POSITION DUTIES:","Fair Labor Standards Act (FLSA) Determination",
              "FLSA Comments/Explanations:", "CONDITIONS OF EMPLOYMENT & NOTES:"]
    return(listOfPieces)
    
def addCols(df, col, listOfItems):
    for num in range(0, len(listOfItems)-1):
        colName= ''.join(x for x in listOfItems[num] if x.isalnum())
        if colName in df.columns:
            colName=colName+"_2"
        print(colName)
        items=df.apply(lambda x: getSection(x[col], listOfItems[num], listOfItems[num+1]),axis=1)
        df[col], df[colName]=items.str[0], items.str[1]
    return(df)
    
def getReplaces(string): 
    if "INTERDISCIPLINARY" in string:
        return("INTERDISCIPLINARY")
    else:
        aList=string.replace("pt:"," pt: ").split(" ")
        paytype=[i[-10:] for i in aList if "-" in i and len(i)>1][-1]
        other=" ".join(aList).replace(paytype,"").strip()
        res = re.sub(r'\d', " ", other)
        try:
            clean=res.split("     ")[1].strip()
        except:
            clean=res.split("     ")[0].strip()
        return(clean)
    
def getPayType(string):
    try: 
        aList=string.replace("pt:"," ").split(" ")
        paytype=[i[-10:] for i in aList if "-" in i and len(i)>1][-1]
        return(paytype)
    except:
        pass
    
def makePIlist():
    positionInformationPieces=['Cyber Workforce',
 'Primary Work Role',
 'Additional Work Role 1',
 'Additional Work Role 2',
 'FLSA',
 'FLSA Worksheet',
 'FLSA Appeal',
 'Bus Code',
 'Mission Category',
 'Work Category',
 'Work Level',
 'Acquisition Position',
 'CAP',
 'Career Category',
 'Career Level',
 'Functional Code',
 'Interdisciplinary',
 'Supervisor Status',
 'PD Status',
 'CONDITION OF EMPLOYMENT',
 'Drug Test Required',
 'Financial Management Certification',
 'Position Designation',
 'Position Sensitivity',
 'Security Access',
 'Emergency Essential',
 'Requires Access to Firearms',
 'Personnel Reliability Position',
 'Information Assurance',
 'Influenza Vaccination',
 'Financial Disclosure',
 'Financial Disclosure',
 'Enterprise Position',
 'POSITION ASSIGNMENT',
 'Competitive Area',
 'Competitive Level',
 'Career Program',
 'Career Ladder PD',
 'Target Grade/FPL',
 'Career Pos 1',
 'Career Pos 2',
 'Career Pos 3',
 'Career Pos 4',
 'Career Pos 5',
 'Career Pos 6']
    positionInformationPieces=[i+":" for i in positionInformationPieces]
    return(positionInformationPieces)
    
def genDropCols():
    dropCols=['PD Text', 'PD Text_change', 'POSITIONINFORMATION','POSITIONINFORMATION_change']
    return(dropCols)
    
def main():
    realPDs=getRealCleanPDs()
    realPDs['PD Text_change']=realPDs['PD Text']
    realPDs= addCols(realPDs, 'PD Text_change', genPieces())
    realPDs['POSITIONINFORMATION_change']=realPDs['POSITIONINFORMATION']
    realPDs=addCols(realPDs, 'POSITIONINFORMATION_change', makePIlist())
    realPDs['Title']=realPDs['ReplacesPD'].apply(getReplaces)
    realPDs['PayType']=realPDs['ReplacesPD'].apply(getPayType)
    keepCols=[i for i in realPDs.columns if i not in genDropCols()]
    finalDF=realPDs[keepCols]
    return(finalDF)

df=main()
#df.to_csv("parsedPDs.csv")
#df.to_excel("parsedPDs.xlsx")
