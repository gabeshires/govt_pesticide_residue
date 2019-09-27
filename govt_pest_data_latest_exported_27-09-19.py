#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import ezodf
import requests
import pathlib 
import re
from bs4 import BeautifulSoup as bs


# In[4]:


parent_urls=[
"https://data.gov.uk/dataset/5d5028ef-9918-4ab7-8755-81f3ad06f308/pesticide-residues-in-food"] #making a list because I think there will be other URLs to add later

def get_soup(url): #integrated function to return parsed HTML
    return bs(requests.get(url).content)


# In[5]:


soup = get_soup(parent_urls[0]) #just taking the first in the url list as the url, currently
file_urls = [a.get('href') for a in soup.find_all('a', href=True) if (re.search('ods',(a.get('href'))))] #getting a list of the links that contain ".ods" filename extension
file_urls


# In[6]:


file_names = [re.search('([A-Za-z_0-9.-]*\.ods)', url).group() for url in file_urls] #extracting the filenames from the urls for later use, when saving locally 
file_names


# In[7]:


#### Functions for this section
# ## 1: Go through urls in file_urls
# ## 2:Download file 
# ## 2a) save into folder "data_files" under current directory 
# ## 2b) name each file the correct filename

def get_path(file_name): #using pathlib to parse path to file and filename
    filetopath = pathlib.Path.cwd() / "data_files" / file_name
    return filetopath

def save_files_locally(file_urls,file_names):
    for url,file_name in zip(file_urls,file_names):
        response = requests.get(url) # getting the raw data from each url
        filetopath = get_path(file_name)
        with open(filetopath, 'wb') as f: # using open method to open a file on system and write the contents
            f.write(response.content) #using with open write to write response.content to local filepath and using filename 
        
save_files_locally(file_urls,file_names) #saves each file in the current directory, in a folder called "data_files"


# In[8]:


def get_doc(filetopath):
    doc = ezodf.opendoc(filetopath)
    return doc

def sheet_names_indexes(doc):
    sheet_name_index = {sheet.name: i for i,sheet in enumerate(doc.sheets)}
    return sheet_name_index

def doc_to_sheet(doc,ind):
    sheet = doc.sheets[ind]
    return sheet

def get_len_of_doc(doc): #gets the number of sheets in the document
    count = len(doc.sheets)
    return count

def identify_categories(row): ### Could use this to put categories as their own column and then fill forward. 
    cells = [cell.value for cell in row]
    if cells[0] != None and all(x is None for x in cells[1:]):
        return True
    else:
        return False

def sheet_to_df(sheet):
    df_dict = {}
    
    for i, row in enumerate(sheet.rows()):
    #     row is a list of cells
    # #     assume the header is on the first row
        if i == 0:
            title = sheet.row(0)[0].value
        elif i == 1:
            # columns as lists in a dictionary
    #         print(cell.value)
    #         df_dict.update({cell.value:[]})
            df_dict = {cell.value:[] for cell in row}
            col_index = [col_title for col_title in df_dict.keys()]
        elif i > 1:
            if identify_categories(row): ###should this be outside the for loop?
                 ### want to do something useful with this but first get it to skipp any category rows
                pass
            for j,cell in enumerate(row):
                df_dict[col_index[j]].append(cell.value)
    return pd.DataFrame(df_dict)

file_name = file_names[0]
filetopath = get_path(file_name)
doc = get_doc(filetopath)
sheet_name_ind = sheet_names_indexes(doc)
sheet_name_ind 


# In[13]:


sheet = doc_to_sheet(doc,1)

df = sheet_to_df(sheet)


# In[14]:


del df[None] # deleting a pd.series "None"
df.fillna(method='ffill', inplace=True) # forward filling the Nones 
df


# In[16]:


# In order to rename the columns in the df, first creating a dictionary of lower case names
renaming_dict ={
old_name : lowercase_name 
    for old_name,lowercase_name 
    in zip(list(df),[new_name.lower().replace(' ','_') 
                     for new_name in list(df)])
}

df = df.rename(columns=renaming_dict) #use the renaming dict to replace column titles in the df


# In[17]:


df.replace({'None were detected above the set RL': 'n/a'}, regex=True, inplace=True)
df


# In[18]:


df['pesticide_residues_found_in_mg/kg_(mrl)'].head(20) # looking at the data in this column


# In[21]:


#splitting the amount detected, name of chem and mrl
#create a second df with just the 'pesticide_residues_found_in_mg/kg_(mrl)' column split into 3 columns

df2=df['pesticide_residues_found_in_mg/kg_(mrl)'].str.extract(r'(.*)\s(\d[\d.]*)\s+\(MRL\s*=\s*(\d[\d.]*)\)')
df2.head(20)


# In[22]:


# Concatinate the df2 columns on to the df1
df = pd.concat([df,df2], axis = 1, sort = False) #new columns are currently 0,1,2
df.rename(columns={0:'chem_name',1:'amount_detected',2:'mrl'},inplace=True) # rename columns 0,1,2 to chem_name, amount_detected, and mrl
df.drop("pesticide_residues_found_in_mg/kg_(mrl)",1, inplace=True) # and deleted the old combined column
df


# In[73]:


df.count() #Returns the number of non-null values in each data frame column


# In[101]:


df.mrl = pd.to_numeric(df.mrl) #converting mrls and amounts detected to numeric values
df.amount_detected = pd.to_numeric(df.amount_detected)
df['amount_detected'].mean()


# In[1]:


g1 = df.groupby( [ "sample_id", "chem_name"] ).count()
g1


# In[102]:


df['chem_name'].value_counts() # shows which is the most common contaminant to be detected


# In[107]:


# regiment_preScore = df['preTestScore'].groupby(df['regiment'])

product_groups = df.groupby(['sample_id','description','chem_name'])
product_groups.sum()


# In[120]:


country_groups = df.groupby('country_of_origin')
# country_df = pd.Dataframe(country_groups.sample_id.count())
country_groups.mean()


# In[ ]:


# df[['col1', 'col2', 'col3', 'col4']].groupby(['col1', 'col2']).agg(['mean', 'count'])

