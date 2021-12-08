# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 09:28:55 2021
this tries to clean BAD PD numbers which have mistakes
@author: HaddadAE
"""
import pandas as pd
import re
import os
import numpy as np
from fuzzywuzzy import fuzz

os.chdir(os.getcwd().replace("code", "data"))
pds=pd.read_csv("aggregatePD.csv", engine='python')
pds['Status'] = np.where(pds['PD Text'].str.len()<5,"Missing","Not Missing")

pds[['CCPO ID', 'Status']].to_excel("PDByStatus.xlsx", index=False)
#########
#########
import pandas as pd
import re
import os
import numpy as np
from fuzzywuzzy import fuzz



os.chdir(os.getcwd().replace("code", "data"))
df=pd.read_excel("PDByStatus.xlsx", engine='openpyxl')
missings=list(df.loc[df['Status']=="Missing"]['CCPO ID'])
notmissing=list(df.loc[df['Status']=="Not Missing"]['CCPO ID'])

dictMissing={}

number=0
for i in missings:
    number=number+1
    for j in notmissing:
        relationship=fuzz.ratio(i,j)
        listi=[]
        if relationship>85:
            listi.append(j)
        if len(listi)>0:
            dictMissing[i]=listi
    if number % 10 ==0:
        print(number)

dfCloseMatch=pd.DataFrame.from_dict(dictMissing, orient='index')

dfCloseMatch=pd.DataFrame.from_dict(dictMissing, orient='index')
dfAll=pd.DataFrame(index=missings)
dfMerge1=dfAll.merge(dfCloseMatch, left_index=True, right_index=True, how='left')
dfMerge1.columns=['Close PDs by Edit Distance']

repeatCPs=[i for i in missings if i[0:2]==i[2:4]]
fixedCPs=[i[2:] for i in repeatCPs]

dfRepeat=pd.DataFrame(index=repeatCPs, data=fixedCPs)
dfRepeat.columns=['First Characters Dropped']
dfMerge2=dfMerge1.merge(dfRepeat, left_index=True, right_index=True, how='left')



spacePDs= [i for i in missings if " " in i]
fixedCPs=[i.replace(" ","") for i in missings if " " in i]


dfSpace=pd.DataFrame(index=spacePDs, data=fixedCPs)
dfSpace.columns=['Space Dropped']
dfMerge3=dfMerge2.merge(dfSpace, left_index=True, right_index=True, how='left')