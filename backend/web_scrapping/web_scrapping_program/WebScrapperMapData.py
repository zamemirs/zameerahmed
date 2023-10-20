import pandas as pd 
import numpy as np
from bs4 import BeautifulSoup
import time
import os
from azure.storage.blob import BlobServiceClient
from io import StringIO
import json
from pyppeteer import launch
from fuzzywuzzy import process
import re
import sys
from datetime import datetime


data = {"FundId":np.array([]),
           "Ticker":np.array([]), 
           "Date":np.array([]),   
           "Record Date":np.array([]), 
           "Ex Date":np.array([]),
           "CapGainDeclarationDate":np.array([]),  
           "Pay Date":np.array([]), 
           "Provider":np.array([]), 
           "EstimateURL":np.array([]),
           "ShortTerm":np.array([]), 
           "LongTerm":np.array([]),
           "TotalCapGains":np.array([]),            
           "ShortTermPercent":np.array([]), 
           "LongTermPercent":np.array([]), 
           "TotalCapGainsPercent":np.array([]), 
           "ShortTermTop":np.array([]),
           "LongTermTop":np.array([]),
           "TotalCapGainsTop":np.array([]),
           "ShortTermPercentTop":np.array([]), 
           "LongTermPercentTop":np.array([]), 
           "TotalCapGainsPercentTop":np.array([]), 
           "NAV":np.array([]), 
           "AddedDate":np.array([]), 
           "Notes":np.array([]),
           "Estimate/ShareClass":np.array([]),
           "FundName":np.array([]),  
           "ShortTermLow":np.array([]),
           "LongTermLow":np.array([]),
           "TotalCapGainsLow":np.array([]), 
           "ShortTermPercentLow":np.array([]),
           "LongTermPercentLow":np.array([]),
           "TotalCapGainsPercentLow":np.array([])
           }



def devisFunds(blob, blob_data, url):
   global df1, column_values

   if(blob.name.split('_')[1] == 'url1.html'):

      html_content = blob_data.readall()
      soup = BeautifulSoup(html_content,'html.parser')
      tables =soup.find_all('table')

      df1 = pd.read_html(StringIO(str(tables[0])), header=0)[0]

      df1.columns = df1.iloc[0]
      df1 = df1.iloc[1:].reset_index(drop=True)

      df1.rename(columns={'Class': 'Share Class', }, inplace=True)
      df1['Share Class'] = df1['Share Class'].replace({'A':'Class A','B':'Class B','C':'Class C','Y':'Class Y','R':'Class R'})
      
      column_values = df1["Fund Name"].drop_duplicates().tolist()
      df1['EstimateURL1'] = url
      
      return [df1, 0]

   else:
      html_content = blob_data.readall()
      soup = BeautifulSoup(html_content,'html.parser')
      tables =soup.find_all('table')

      i=0
      combined_tables = []
      for table in tables[1:9]:
         df = pd.read_html(StringIO(str(table)))[0].ffill()
         df.insert(0, "Fund Name", [column_values[i] for _ in range(len(df["Share Class"]))])
         i+=1

         '''df.rename(columns={'Short-term Capital Gain': 'Short-term Capital Gain $', }, inplace=True)
         df.rename(columns={'Long-term Capital Gain': 'Long-term Capital Gain $', }, inplace=True)'''
         combined_tables.append(df.replace({'-': ''}))

      df2 = pd.concat(combined_tables, ignore_index=True).ffill()
      df2['EstimateURL2'] = url
      
      merged_df = pd.merge(df1, df2, on=['Fund Name', 'Share Class'], how= 'left', suffixes=('_df1', '_df2'))
      
      return [merged_df, 1]



def cohenandsteers(blob_data, url):
   json_data = json.loads(blob_data.read())
   
   combined_tables = []

   for table in json_data['tables']:
      header = []
      rows = [['' for i in range(table['row_count']-1)] for j in range(table['column_count'])]

      for cell in table['cells']:
         if(cell['kind'] == "columnHeader"):
            header.append(cell['content'].replace('(10/31/22)','(10/31/2022)'))
            
         else:
            rows[cell['column_index']][cell['row_index']-1] = cell['content'].replace('\n:unselected:', '').replace('–C', '– C')
      
      dict_table= {}
      
      for i in range(len(header)):
        dict_table[header[i]] = rows[i]

      df = pd.DataFrame(dict_table)
      
      share_Class = df['Fund Name'].str.split('(').str[0].str[2:-1].tolist()
      fund_Ticker = df['Fund Name'].str.split(': ').str[1].str[:-1].tolist()

      df.insert(1, "Share Class", share_Class)
      df.insert(2, "Fund Ticker", fund_Ticker)

      mask = df['Fund Name'].str.contains('|'.join(['Class', 'Nasdaq:','Fund Inc.']))
      df.loc[mask, 'Fund Name'] = pd.NA
      df['Fund Name'] = df['Fund Name'].ffill()

      mask = df['Fund Ticker'].str.contains("").ffill(False)
      df = df[mask]

      combined_tables.append(df)

   final_df = pd.concat(combined_tables, ignore_index=True)
   final_df['EstimateURL'] = url

   return final_df



def ishares(blob, blob_data, url):

   if(blob.name.split('_')[1] == 'url1.html'):
      html_content = blob_data.readall()
      soup = BeautifulSoup(html_content,'html.parser')
      tables =soup.find_all('table')

      #for table in tables:

      df1 = pd.read_html(StringIO(str(tables[16])))[0]
      df1[['Fund Name', 'Fund Ticker']] = df1['Fund Name'].str.extract(r'(.*?)\s+\((.*)\)', expand=True)
      df1['Provider Name'] = 'iShares'
      df1['EstimateURL'] = url
   return df1.replace({'–': ''})



def bridgebuilders(blob, blob_data, url):
   if(blob.name.split('.')[1] == 'pdf'):
      json_data = json.loads(blob_data.read())
      
      header = []
      rows = [['' for i in range(json_data['tables'][0]['row_count']-1)] for j in range(json_data['tables'][0]['column_count'])]

      for cell in json_data['tables'][0]['cells']:
         if(cell['kind'] == "columnHeader"):
            header.append(cell['content'])

         else:
            rows[cell['column_index']][cell['row_index']-1] = cell['content'].replace('-',' ')
            
      dict_table= {}
      for i in range(len(header)):
         dict_table[header[i]] = rows[i] 
      
      for pair in json_data['key_value_pairs']:
         dict_table[pair['key']['content']] = pair['value']['content']

      df = pd.DataFrame(dict_table)
      df['EstimateURL'] = url

      return df
   


def lyricalam(blob_data, url):
   json_data = json.loads(blob_data.read())

   header = []
   rows = [['' for i in range(json_data['tables'][0]['row_count']-1)] for j in range(json_data['tables'][0]['column_count'])]

   for cell in json_data['tables'][0]['cells']:
      if(cell['kind'] == "columnHeader"):
         header.append(cell['content'])

      else:
         rows[cell['column_index']][cell['row_index']-1] = cell['content'].replace('-',' ')
         
   dict_table= {}
   for i in range(len(header)):
      dict_table[header[i]] = rows[i] 
   
   for pair in json_data['key_value_pairs']:
      dict_table[pair['key']['content']] = pair['value']['content']

   df = pd.DataFrame(dict_table)
   df['EstimateURL'] = url

   return df
   


def capitalgroup(blob, blob_data, url):
   if(blob.name.split('_')[1] == 'url1.html'):

      html_content = blob_data.readall()
      soup = BeautifulSoup(html_content,'html.parser')
      tables =soup.find_all('table')

      combined_tables = []

      for i in [0, 1, 2, 3, 4]:
         df = pd.read_html(StringIO(str(tables)))[i].replace('—','')
         df = df.dropna(axis=0, how='all')
         df.columns = ['Fund Name', 'Ex-date', 'Record date', 'Payment date', 'Long term Cap $', 'Short term Cap $']
         
         df['Ex-date'] = df['Ex-date'].apply(lambda x: f"{x}/22" if len(x) <= 5 else x)
         df['Record date'] = df['Record date'].apply(lambda x: f"{x}/22" if len(x) <= 5 else x)
         df['Payment date'] = df['Payment date'].apply(lambda x: f"{x}/22" if len(x) <= 5 else x)

         df['Fund Name'] = df['Fund Name'].str.replace('–','-').str.replace('[^a-zA-Z0-9\s-]', '', regex=True)

         combined_tables.append(df)

      final_df = pd.concat(combined_tables, ignore_index=True)
      final_df['EstimateURL'] = url

      return final_df.ffill()

   else:
      html_content = blob_data.readall()
      soup = BeautifulSoup(html_content,'html.parser')
      tables =soup.find_all('table')

      df = pd.read_html(StringIO(str(tables)), header = 0)[0]
      df.drop(df.columns[[1, 5, 6]], axis=1, inplace=True)

      df['Fund Name'] = df['Fund Name'].str.replace(r'\s+(\S+\s+\S+)$', '', regex=True)
      df.dropna(subset=df.columns[1:], how='all', inplace=True)
      df['EstimateURL'] = url

      return df



def lordabbett(blob, blob_data, url):
   
   html_content = blob_data.readall()
   soup = BeautifulSoup(html_content,'html.parser')
   tables =soup.find_all('table')

   if('MUTUAL_FUND' in blob.name or blob.name.split('.')[0][-1:] in ['a', 'i', 'u']):
      df = pd.read_html(StringIO(str(tables)), header = 0)[0]
      df.rename(columns={'Unnamed: 0': 'Fund Name'}, inplace=True)#, 'Short Term': 'Short Term Cap $', 'Short Term.1': 'Short Term Cap %', 'Long Term': 'Long Term Cap $', 'Long Term.1': 'Long Term Cap %', 'Ex, Reinvest and Payable Date': 'Ex Date'

   else:
      df = pd.read_html(StringIO(str(tables)), header = 0)[1]
      df.rename(columns={'Unnamed: 0': 'Fund Name'}, inplace=True)#, 'Estimated Short Term Capital Gains Range': 'Short Term Cap %', 'Estimated Long Term Capital Gains Range': 'Long Term Cap %', 'Ex, Reinvest and Payable Date': 'Ex Date'}, inplace=True)

   #df["Payable Date"] = df['Ex Date']
   df = df.iloc[4:].replace('-','')

   df[['Fund Name', 'Share Class', 'Fund Ticker']] = df['Fund Name'].str.extract(r'^(.*?)\s*\((.*?)\)\s*(\S+)\s.*$').replace('Inception','')
   df['Share Class'] = 'Class ' + df['Share Class']
   df['EstimateURL'] = url
   #print(df)
   return df.ffill()



def fidelity(blob_data, url):

   html_content = blob_data.readall()
   soup = BeautifulSoup(html_content,'html.parser')
   tables =soup.find_all('table')

   df = pd.read_html(StringIO(str(tables)), header = 0)[0]

   df.columns = df.iloc[0]
   df = df.iloc[1:].reset_index(drop=True)

   #df.rename(columns={'Short-Term ($)': 'Short Term Cap $', 'Long-Term ($)': 'Long Term Cap $', 'Total ($)': ''}, inplace=True)   

   df['Share Class'] = df['Fund Name'].str.extract(r'\b([A-Z]\d*|[A-Z])\b')
   df['Share Class'] = 'Class ' + df['Share Class']
   df['Fund Ticker'] = df['Fund Name'].str.extract(r'Symbol\s+([A-Za-z0-9]+)')
   df['Fund Name'] = df['Fund Name'].str.extract(r'^(.*?)(?:-|Cl )')
   df['EstimateURL'] = url

   return df.ffill()



def baronfunds(blob_data, url):

   html_content = blob_data.readall()
   soup = BeautifulSoup(html_content,'html.parser')
   tables =soup.find_all('table')
   
   caption1 = list(filter(None, tables[3].find('caption').get_text().replace('\n', '').split('  ')))
   df1 = pd.read_html(StringIO(str(tables)))[3]
  
   df1.insert(0, "Fund Name", [caption1[0] for _ in range(len(df1))])
   df1.insert(1, "Fund Ticker", [caption1[1][2:-1] for _ in range(len(df1))])
   
   combined_tables = [df1]

   for i in [2, 4, 5]:
      caption2 = tables[i].find('caption').get_text().replace('-', '').strip().split('  ')
      df2 = pd.read_html(StringIO(str(tables)))[i]

      df2.rename(columns={'Fund': 'Fund Name'}, inplace=True)
      df2[['Fund Name', 'Fund Ticker']] = df2['Fund Name'].str.extract(r'^(.*?)\s*\((.*?)\)$')

      df2.insert(1, ' '.join(caption2[0].split(' ')[:2]), [caption2[0].split(' ')[2] for _ in range(len(df2))])
      df2.insert(2, ' '.join(caption2[1].split(' ')[:2]), [caption2[1].split(' ')[2] for _ in range(len(df2))])
      df2.insert(3, ' '.join(caption2[2].split(' ')[:2]), [caption2[2].split(' ')[2] for _ in range(len(df2))])

      combined_tables.append(df2)

   final_df = pd.concat(combined_tables, ignore_index=True)
   final_df['EstimateURL'] = url

   return final_df.ffill()



def parnassus(blob, blob_data, url):

   if(blob.name.split('.')[1] == 'html'):

      html_content = blob_data.readall()
      soup = BeautifulSoup(html_content,'html.parser')
      tables =soup.find_all('table')
      
      # df = pd.read_html(str(tables))[1].iloc[2:-1]
      df = pd.read_html(StringIO(str(tables)))[1].iloc[2:-1]

      for col in df.columns.to_list():
         df[col] = df[col].str.replace(col + '  ','')

      mask = df.apply(lambda row: row.str.contains('2023|Income Dividend')).any(axis=1)
      df = df[~mask]
      df['EstimateURL'] = url

      return df.ffill()



def janushenderson(blob, blob_data, url):

   json_data = json.loads(blob_data.read())
   combined_tables = []

   for i in range(len(json_data['tables'])):
      header = []
      rows = [['' for i in range(json_data['tables'][i]['row_count']-1)] for j in range(json_data['tables'][i]['column_count'])]

      for cell in json_data['tables'][i]['cells']:
         if(cell['kind'] == "columnHeader"):
            header.append(cell['content'])

         else:
            rows[cell['column_index']][cell['row_index']-1] = cell['content'].replace(' Shares', '').replace('\n:selected:', '').replace('\n:unselected:', '')

      dict_table= {}

      if(blob.name.split('_')[1] != 'url2.pdf'):
         dict_table['Share Class'] = 'Class ' + header[-3][0]

      header = ['CUSIP', 'Ticker', 'Fund', 'Investment Income', 'Short-Term Capital Gain', 'Total Dividends', 'Capital Gain Distributions', 'Total Dividends & Distributions']
      
      for i in range(len(header)):
         dict_table[header[i]] = rows[i] 

      df = pd.DataFrame(dict_table)
      
      if(blob.name.split('_')[1] == 'url2.pdf'):
         df['Share Class'] = df['Fund'].str.extract(r' - (Class [A-Z])$')
         df['Fund'] = df['Fund'].str.extract(r'^(.*) - Class [A-Z]$')

      df = df.iloc[2:]
      df['Fund'] = df['Fund'].str.replace(r'^\(\d+\)\s*', '', regex=True)

      combined_tables.append(df)
      
   final_df = pd.concat(combined_tables, ignore_index=True)
   dates = re.findall(r"December \d+, \d+", json_data['content'])

   final_df['Pay Date'] = dates[0]

   final_df['Record Date'] = dates[1]
   final_df['EstimateURL'] = url

   return final_df.ffill()



def putnam(blob, blob_data, url):

   if(blob.name.split('.')[1] == 'html'):

      html_content = blob_data.readall()
      soup = BeautifulSoup(html_content,'html.parser')
      tables =soup.find_all('table')

      df = pd.read_html(StringIO(str(tables)))
   
   else:
      json_data = json.loads(blob_data.read())
      
      combined_tables = []

      for table in json_data['tables']:
         header = []
         rows = [['' for i in range(table['row_count']-1)] for j in range(table['column_count'])]

         for cell in table['cells']:
            if(cell['kind'] == "columnHeader"):
               header.append(cell['content'])

            else:
               rows[cell['column_index']][cell['row_index']-1] = cell['content'].replace('\n:selected:', '')

         dict_table= {}
         for i in range(len(header)):
            try:
                  dict_table[header[i]] = rows[i]
            except:
                  pass
         
         df = pd.DataFrame(dict_table).replace('', np.nan)

         #df.rename(columns={'Putnam fund name': 'Fund Name'}, inplace=True)#, 'Class': 'Share Class', 'Short-term cap gain': 'Short Term Cap $', 'Long-term cap gain': 'Long Term Cap $', 'Total': ''
         
         df['Putnam fund name'] = df['Putnam fund name'].ffill()
         df.dropna(subset=df.columns[1:], how='all', inplace=True)
         
         combined_tables.append(df)
      
      final_df = pd.concat(combined_tables, ignore_index=True)
      final_df['EstimateURL'] = url

      return final_df.ffill()



def hartfordfunds(blob, blob_data, url):

   if(blob.name.split('_')[1] == 'url1.pdf'):
      resp_data = json.loads(blob_data.read())
      
      combined_Tables = []
      #print(len(resp_data['tables']))
      for i in range(2):

         rows = [['' for _ in range(resp_data['tables'][i]['row_count'])] for _ in range(resp_data['tables'][i]['column_count'])]

         for cell in resp_data['tables'][i]['cells']:
            if cell['kind'] == "content":
               rows[cell['column_index']][cell['row_index']] = cell['content'].replace('$ -',  '')

         header = ['Fund Name', 'Class | * NAV Share', 'Short Term Capital Gains Per Share', 'Long Term Capital Gains Per Share', 'Short Term Capital Gains Percentage of NAV', 'Long Term Capital Gains Percentage of NAV', 'Total Capital Gains Percentage of NAV']

         dict_table = {}
         for i, col_name in enumerate(header):
            try:
               dict_table[col_name] = rows[i][:]
            except:
               pass

         df = pd.DataFrame(dict_table).iloc[3:].replace('', np.nan)
         df = df.dropna(axis=0, how='all', subset=df.columns[1:]).ffill()

         combined_Tables.append(df)
      
      final_df = pd.concat(combined_Tables, ignore_index=True)
      final_df['EstimateURL'] = url

      return final_df.ffill()
      

   else:
      resp_data = json.loads(blob_data.read())

      header = []

      rows = [['' for _ in range(resp_data['tables'][0]['row_count'])] for _ in range(resp_data['tables'][0]['column_count'])]

      for cell in resp_data['tables'][0]['cells']:
         if cell['kind'] == "columnHeader" and cell['content'] not in ['Final']:
            header.append(cell['content'].replace('\n', ' '))
         else:
            rows[cell['column_index']][cell['row_index']] = cell['content']

      header[1] = 'Share Class'

      dict_table = {}
      for i, col_name in enumerate(header):
         try:
            dict_table[col_name] = rows[i][:]
         except:
            pass

      df = pd.DataFrame(dict_table).iloc[2:]
      df['EstimateURL'] = url

      return df.ffill()



def doubleline(blob, blob_data, url):
   
   json_data = json.loads(blob_data.read())

   header = []
   rows = [['' for i in range(json_data['tables'][0]['row_count']-1)] for j in range(json_data['tables'][0]['column_count'])]

   for cell in json_data['tables'][0]['cells']:
      if(cell['kind'] == "columnHeader"):
         header.append(cell['content'])

      else:
         rows[cell['column_index']][cell['row_index']-1] = cell['content'].replace('─\n:unselected:', '').replace(':unselected:', '').replace('─', '')

   dict_table= {}
   for i in range(len(header)):
         dict_table[header[i]] = rows[i]


   header = []
   rows = []
   for cell in json_data['tables'][1]['cells']:
      if(cell['kind'] == "columnHeader" and cell["column_index"] != 0):
         header.append(cell['content'])
      elif(cell["column_index"] != 0):
         rows.append(cell['content'])
         
   for i in range(len(header)):
      dict_table[header[i]] = rows[i]

   df = pd.DataFrame(dict_table)
   
   if('Long-Term Capital Gains Distributions ($/Share) 1' in df.columns):
      df['Long-Term Capital Gains Distributions ($/Share) 1'] = df['Long-Term Capital Gains Distributions ($/Share) 1'].str.split(' ').str[0]
   
   df['EstimateURL'] = url

   return df.ffill()



def getweburl(source):
    parts = source.split("/")

    # First part corresponds to value1, second part corresponds to value2
    value1 = parts[1]
    value2 = parts[2].split(".")[0]  # Remove the ".pdf" extension

    #print("Value 1:", value1)
    #print("Value 2:", value2)

    # TODO : fetch file from DB or azure or cloud
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_json_path = os.path.join(BASE_DIR, 'web_scrapping_program/input.json')

    with open(input_json_path, 'r') as f:
        config_list = json.load(f)

    df = pd.DataFrame(config_list)

    if ((df['raw_filename'] == value2) & (df['folder_name'] == value1)).any():
      # Use .any() to check if any row meets the condition
      return str(df.loc[(df['raw_filename'] == value2) & (df['folder_name'] == value1), 'url'].values[0])

    elif (df['folder_name'] == value1).any():
      return str(df.loc[df['folder_name'] == value1, 'url'].values[0])

    else:
      return None
    


def matchingHeader(column_name, target_columns, lookUpTable):
   
   lookUpTable_lower = [val.lower() for val in lookUpTable[column_name]]

   for column in target_columns:
      if(column.lower() in lookUpTable_lower):
         return column
   return None



def data_Map(data, df, provider):

   # TODO : fetch file from DB or azure or cloud
   BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   lookup_json_path = os.path.join(BASE_DIR, 'web_scrapping_program/lookUpTable.json')

   with open(lookup_json_path, 'r') as f:
      lookUpTable = json.load(f)

   exclude = ''
   if("Unnamed: 0" in df.columns.to_numpy()):
      temp = np.array(df["Unnamed: 0"].values)[0].split(" ")

      if("Fund" in temp or "Portfolio" in temp):
         data["FundName"] = np.append(data["FundName"], np.array(df["Unnamed: 0"].values))
         exclude = "FundName"

      else:
         data["Provider"] = np.append(data["Provider"], np.array(df["Unnamed: 0"].values))
         exclude = "Provider"


   df = df.map(lambda x: str(x).strip() if (isinstance(x, str) and x is not None) else x)

   for key in data.keys():
      return_value = matchingHeader(key, df.columns.to_list(), lookUpTable)
      
      if(return_value):
         df[return_value] = df[return_value].replace('None Expected', '')
         data[key] = np.append(data[key], np.array(df[return_value].values))

      elif(key != exclude):
         if(key == "Provider"):
            data[key] = np.append(data[key], np.array([provider for i in range(len(df.index))]))

         else:
            data[key] = np.append(data[key], np.array(['' for i in range(len(df.index))]))
   
   return data



def splitHighLow(data):
   
   for index in range(len(data['ShortTermPercent'])):

      split_data_1 = str(data['ShortTermPercent'][index]).split('-') if '-' in str(data['ShortTermPercent'][index]) else str(data['ShortTermPercent'][index]).split('to')
      if(len(split_data_1)>1):
         if data['ShortTermPercentLow'][index] == '': data['ShortTermPercentLow'][index] = split_data_1[0]

         if data['ShortTermPercentTop'][index] == '': data['ShortTermPercentTop'][index] = split_data_1[-1]

         data['ShortTermPercent'][index] = ''


      split_data_2 = str(data['LongTermPercent'][index]).split('-') if '-' in str(data['LongTermPercent'][index]) else str(data['LongTermPercent'][index]).split('to')
      if(len(split_data_2)>1):
         if data['LongTermPercentLow'][index] == '': data['LongTermPercentLow'][index] = split_data_2[0]

         if data['LongTermPercentTop'][index] == '': data['LongTermPercentTop'][index] = split_data_2[-1] 

         data['LongTermPercent'][index] = ''


      split_data_3 = str(data['ShortTerm'][index]).split('-') if '-' in str(data['ShortTerm'][index]) else str(data['ShortTerm'][index]).split('to')
      if(len(split_data_3)>1):
         if data['ShortTermLow'][index] == '': data['ShortTermLow'][index] = split_data_3[0]

         if data['ShortTermTop'][index] == '': data['ShortTermTop'][index] = split_data_3[-1]

         data['ShortTerm'][index] = ''
         

      split_data_4 = str(data['LongTerm'][index]).split('-') if '-' in str(data['LongTerm'][index]) else str(data['LongTerm'][index]).split('to')
      if(len(split_data_4)>1):
         if data['LongTermLow'][index] == '': data['LongTermLow'][index] = split_data_4[0]

         if data['LongTermTop'][index] == '': data['LongTermTop'][index] = split_data_4[-1] 

         data['LongTerm'][index] = ''


      split_data_5 = str(data['TotalCapGains'][index]).split('-') if '-' in str(data['TotalCapGains'][index]) else str(data['TotalCapGains'][index]).split('to')
      if(len(split_data_5)>1):
         if data['TotalCapGainsLow'][index] == '': data['TotalCapGainsLow'][index] = split_data_5[0]

         if data['TotalCapGainsTop'][index] == '': data['TotalCapGainsTop'][index] = split_data_5[-1] 

         data['TotalCapGains'][index] = ''

   
      split_data_6 = str(data['TotalCapGainsPercent'][index]).split('-') if '-' in str(data['TotalCapGainsPercent'][index]) else str(data['TotalCapGainsPercent'][index]).split('to')
      if(len(split_data_6)>1):
         if data['TotalCapGainsPercentLow'][index] == '': data['TotalCapGainsPercentLow'][index] = split_data_6[0]

         if data['TotalCapGainsPercentTop'][index] == '': data['TotalCapGainsPercentTop'][index] = split_data_6[-1] 

         data['TotalCapGainsPercent'][index] = ''
  
   return data



def writeToBlob(data):
   dtFrm = pd.DataFrame(data).ffill().map(lambda x: str(x).strip())
   
   dtFrm['Date']=datetime.now()
   dtFrm['NAV']=''
   dtFrm['AddedDate']=''
   #date format
   for col in ['Record Date', 'Date', 'Ex Date', 'Pay Date']:
      dtFrm[col] = pd.to_datetime(dtFrm[col], format='mixed', errors='coerce').dt.strftime('%m/%d/%Y')

   # add $ and % 
   columns = ['TotalCapGains', 'TotalCapGainsPercent', 
              'TotalCapGainsTop', 'TotalCapGainsLow', 'TotalCapGainsPercentTop','TotalCapGainsPercentLow',
              'ShortTerm','LongTerm','ShortTermPercent','LongTermPercent',
              'ShortTermTop','ShortTermLow','LongTermTop','LongTermLow','ShortTermPercentTop','ShortTermPercentLow','LongTermPercentTop','LongTermPercentLow']
   for col in columns:
      if 'Percent' not in str(col):
         dtFrm[col] = dtFrm[col].apply(lambda x: '$' + str(x) if not str(x).strip().startswith('$') and (x != '' and x is not None) else x)
      if 'Percent' in str(col):
         dtFrm[col] = dtFrm[col].apply(lambda x: str(x) + '%' if not str(x).strip().endswith('%') and (x != '' and x is not None) else x)

   blob_service = BlobServiceClient.from_connection_string(conn_str=adls_connection_string)
   container_client = blob_service.get_container_client(container_name)
   
   newName = {'Record Date': 'CapGainRecordDate', 'Pay Date': 'CapGainPayableDate', 'Ex Date': 'CapGainExDate'}
   dtFrm.rename(columns= newName, inplace=True)
   dtFrm.replace('', None, inplace=True)
   #dtFrm = dtFrm.ffill('\\N')

   buffer_file = StringIO()
   dtFrm.to_csv(buffer_file, index=False)
   csv_data = buffer_file.getvalue().encode('utf-8') 

   file_name = f"output\\data_map_{timestr}.csv"
   container_client.upload_blob(name=file_name, data=csv_data, overwrite=True)

   if not os.path.exists(base_directory):
      os.makedirs(base_directory)

   #outputfile = f"D:\\Python\\data_map.csv"
   outputfile = os.path.join(base_directory, f"data_map_{timestr}.csv")
   save_file = open(outputfile,'w+')
   save_file.write(buffer_file.getvalue())
   buffer_file.close()
   save_file.close()




if __name__ == "__main__":

   timestr = '20231017120050' #input("Folder Name: ")
   input_lines = sys.stdin.readlines()

   # Processing each line of input
   for line in input_lines:
      input_data = line.strip()
      #print(f"Received input: {input_data}")
      timestr=input_data

   base_directory = os.path.join(os.getcwd(), "mappedoutput")
   adls_connection_string ="DefaultEndpointsProtocol=https;AccountName=webscrapinginvesco0;AccountKey=8/jjkAZUFstIktZ+dHd2Mj2IAo2BRnaFh0kxXoh9pHYZAh1XmwqQn1+vDipHX6vK6wgXj7CNxzXT+AStRIVekw==;EndpointSuffix=core.windows.net"
   container_name ="raw"

   blob_service = BlobServiceClient.from_connection_string(conn_str=adls_connection_string)

   container_client = blob_service.get_container_client(container_name)

   blobs_list = container_client.list_blobs(f"{timestr}")


   for blob in blobs_list:
      try:
         print("------------------------------------------------------------------")
         print("blob name", blob.name)
         blob_client = blob_service.get_blob_client(container_name, blob.name)
         blob_data = blob_client.download_blob()

         print(blob.name.split('/')[1]+'/'+blob.name.split('/')[2])
         
         if(blob.name.split('/')[1] == 'davisfunds'):
            
            returnData = devisFunds(blob, blob_data, getweburl(blob.name))

            if (returnData[1] == 1):
               data = data_Map(data, returnData[0], 'Davis Funds')


         if(blob.name.split('/')[1] == 'cohenandsteers'):
            
            returnData = cohenandsteers(blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Cohen and steers')


         if(blob.name.split('/')[1] == 'ishares'):
            
            returnData = ishares(blob, blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'iShares')


         if(blob.name.split('/')[1] == 'bridgebuilders' and blob.name.split('.')[1] == 'pdf'):
            
            returnData = bridgebuilders(blob, blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Bridge Builders')


         if(blob.name.split('/')[1] == 'lyricalam'):
            
            returnData = lyricalam(blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Lyricalam')
         

         if(blob.name.split('/')[1] == 'capitalgroup'):
            
            returnData = capitalgroup(blob, blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Capital Group')


         if(blob.name.split('/')[1] == 'lordabbett'):
            
            returnData = lordabbett(blob, blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Lord Abbett')


         if(blob.name.split('/')[1] == 'fidelity'):
            
            returnData = fidelity(blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Fidelity')
            
            
         if(blob.name.split('/')[1] == 'baronfunds'):
            
            returnData = baronfunds(blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Baron Funds')
         

         if(blob.name.split('/')[1] == 'parnassus' and blob.name.split('.')[1] == 'html'):
            
            returnData = parnassus(blob, blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Parnassus')

         
         if(blob.name.split('/')[1] == 'janushenderson'):
            
            returnData = janushenderson(blob, blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Janus Henderson')


         if(blob.name.split('/')[1] == 'putnam' and blob.name.split('.')[1] == 'pdf'):
            
            returnData = putnam(blob, blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Putnam')
         

         if(blob.name.split('/')[1] == 'hartfordfunds'):
            
            returnData = hartfordfunds(blob, blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'Hartford Funds')
         

         if(blob.name.split('/')[1] == 'doubleline' and '2022' in blob.name.split('/')[2]):
            
            returnData = doubleline(blob, blob_data, getweburl(blob.name))

            data = data_Map(data, returnData, 'DoubleLine')
      

      except Exception as e:

         print("Exception : ", str(e),'\n')
         
      
   data = splitHighLow(data)
   writeToBlob(data)
   print("RESULT:"f"{timestr}")





