#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import ezodf


# In[4]:


# wks = pd.read_excel('http://data.defra.gov.uk/PRIF/Q1_2018_quarterly_data.ods', engine='odf')

doc = ezodf.opendoc('Q1_2018_quarterly_data.ods')

print("Spreadsheet contains %d sheet(s)." % len(doc.sheets))
for sheet in doc.sheets:
    print("-"*40)
    print("   Sheet name : '%s'" % sheet.name)
    print("Size of Sheet : (rows=%d, cols=%d)" % (sheet.nrows(), sheet.ncols()) )


# In[5]:


# convert the first sheet to a pandas.DataFrame
sheet = doc.sheets[3]
product = sheet.name
df_dict = {}
for i, row in enumerate(sheet.rows()):
#     row is a list of cells
# #     assume the header is on the first row
    if i == 1:
        # columns as lists in a dictionary
#         print(cell.value)
#         df_dict.update({cell.value:[]})
        df_dict = {cell.value:[] for cell in row}
# df_dict
product


# In[6]:


#         # create index for the column headers
for i,row in enumerate(sheet.rows()):
    if i == 0:
        continue
    elif i == 1:
        col_index = [cell.value for cell in row]
#         print([cell.value for cell in row])
        continue
    for j,cell in enumerate(row):
#         print (j,cell.value)
        df_dict[col_index[j]].append(cell.value)
# # # and convert to a DataFrame
# df_dict
# df = pd.DataFrame(df_dict)
df = pd.DataFrame(df_dict)


# In[2]:


pwd


# In[7]:


del df[None]
df


# In[8]:


df.fillna(method='ffill', inplace=True)
df


# In[9]:


renaming_dict = {
old_name : new_name 
    for old_name,new_name 
    in zip(list(df),[new_name.lower().replace(' ','_') 
                     for new_name in list(df)])
}

df = df.rename(columns=renaming_dict)


# In[10]:


#splitting the amount detected, name of chem and mrl

# df['pesticide_residues_found_in_mg/kg_(mrl)']
df.replace({'None were detected above the set RL': 'n/a'}, regex=True, inplace=True)
df


# In[11]:


df['pesticide_residues_found_in_mg/kg_(mrl)'].head(20)


# In[12]:


# df['pesticide_residues_found_in_mg/kg_(mrl)'].str.extract(r'(?P<mrl>\(MRL = \d.?\d+?\))') ## this works 
# df['pesticide_residues_found_in_mg/kg_(mrl)'].str.extract(r'(?P<mrl>\d+\.?\d+?)')
#(?P<chem_detected>^\w+\b[^0-9])
#(r'(?P<mrl>\((MRL = )(\d+.?\d*?)\))')
# s.str.extract(r'(?P<letter>[ab])(?P<digit>\d)')                                                                     
# df.row.str.extract('(?P<fips>\d{5})((?P<state>[A-Z ]*$)|(?P<county>.*?), (?P<state_code>[A-Z]{2}$))')


df2=df['pesticide_residues_found_in_mg/kg_(mrl)'].str.extract(r'(.*)\s(\d[\d.]*)\s+\(MRL\s*=\s*(\d[\d.]*)\)')
df2
# df['mrl']=df['pesticide_residues_found_in_mg/kg_(mrl)'].str.split('(', n=-1, expand=True)
# df['ad'] = df['pesticide_residues_found_in_mg/kg_(mrl)'].str.split(' ', n=1, expand=True)
# df["chemical_detected"],df['amount_detected'],
# df.mrl


# In[13]:


df = pd.concat([df,df2], axis = 1, sort = False) 
# df.drop([0,1,2], 1, inplace=True)
df


# In[14]:


df.rename(columns={0:'chem_name',1:'amount_detected',2:'mrl'},inplace=True)


# In[15]:


df.drop("pesticide_residues_found_in_mg/kg_(mrl)",1, inplace=True)

