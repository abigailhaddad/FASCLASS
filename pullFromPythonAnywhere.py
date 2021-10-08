# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 11:43:31 2021
This is for pulling my FASCLASS xlsx files from pythonanywhere if you have the APIkey
@author: HaddadAE
"""
import os
import requests
import pandas as pd

fileName='APIkey.txt'

def pullToken(fileName):
    with open(fileName) as f:
        lines = f.readlines()
    token=lines[0][1:-1]
    return(token)

def listOfFiles(token):
    username='abigailhaddad'
    pythonanywhere_host = "www.pythonanywhere.com"
    url = f"https://{pythonanywhere_host}/api/v0/user/{username}/files/path/home/{username}/fasclassBetter/data/"
    resp = requests.get(url,
    headers={"Authorization": "Token {api_token}".format(api_token=token)}, verify=False)
    listOfFiles=list(resp.json().keys())
    filesToKeep=[i for i in listOfFiles if "textScrape" in i and ".xlsx" in i]
    return(filesToKeep, url)
    
def pullFile(file, token, url):
    print(file)
    resp = requests.get(url+file,
    headers={"Authorization": f"Token {token}"}, verify=False)
    with open(file, 'wb') as output:
        output.write(resp.content)
    
def pullFiles(fileName):
    os.chdir(os.getcwd().replace("code", "data"))
    token=pullToken(fileName)
    filesToKeep, url=listOfFiles(token)
    for file in filesToKeep:
        pullFile(file, token, url)
        
def readAggregate():
    os.chdir(os.getcwd().replace("code", "data"))
    files=[pd.read_excel(i) for i in os.listdir() if "textScrape" in i]
    wholeDF=pd.concat(files)
    return(wholeDF)
    
pullFiles(fileName)
df=readAggregate()
    