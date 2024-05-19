import requests
import json
import sqlite3 as db
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

wikipedia_url = 'https://web.archive.org/web/20230908091635%20/https://en.wikipedia.org/wiki/List_of_largest_banks'
exchange_rate_csv = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-PY0221EN-Coursera/labs/v2/exchange_rate.csv'
log_file = 'code_log.txt'
csv_load_file = 'Largest_banks_data.csv'
table_name = 'Largest_banks'
db_name = 'Banks.db'

def log_progress(message):
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(log_file,"a") as f:
        f.write(timestamp + ' : ' + message + '\n')

def extract():
  extract_df = pd.DataFrame(columns=["Name", "MC_USD_Billion"])
  soup = BeautifulSoup(requests.get(wikipedia_url).text, 'html.parser')

  bank_table = soup.find('table', {'class': 'wikitable'})
  bank_table_body = bank_table.find('tbody')

  print(bank_table_body)

  for row in bank_table_body.find_all('tr')[1:]:
    columns = row.find_all('td')
    bank_name = columns[1].get_text(strip=True)
    market_cap = float(columns[2].get_text(strip=True))
    extract_df = pd.concat([extract_df,pd.DataFrame([{'Name':bank_name,'MC_USD_Billion':market_cap}])],ignore_index=True)

  log_progress('Data extraction complete. Initiating Transformation process')

  return extract_df

def transform(data_frame):

  exchange_data = pd.read_csv(exchange_rate_csv)

  eur_rate = exchange_data.at[0,'Rate']
  gbp_rate = exchange_data.at[1,'Rate']
  inr_rate = exchange_data.at[2,'Rate']

  data_frame['MC_GBP_Billion'] = round((data_frame['MC_USD_Billion'] * float(gbp_rate)),2)
  data_frame['MC_EUR_Billion'] = round((data_frame['MC_USD_Billion'] * float(eur_rate)),2)
  data_frame['MC_INR_Billion'] = round((data_frame['MC_USD_Billion'] * float(inr_rate)),2)

  log_progress('Data transformation complete. Initiating Loading process')

  return data_frame

def load_to_csv(bank_data,csv_load_file):
  bank_data.to_csv(csv_load_file)
  log_progress('Data saved to CSV file')

def load_to_db(bank_data,conn,table_name):
  bank_data.to_sql(table_name,conn,if_exists='replace', index=False)

def run_queries(query_statement,conn):
  query_output = pd.read_sql(query_statement, conn)
  print(query_statement)
  print(query_output.to_string())


pd.set_option('display.max_columns', None)
bank_data = extract()
print('extracted: ')
print(bank_data.to_string())
bank_data = transform(bank_data)
print('transformed: ')
print(bank_data.to_string())
print('loading...')
load_to_csv(bank_data,csv_load_file)
load_to_db(bank_data,db.connect(db_name),table_name)
log_progress('Data loaded to Database as a table, Executing queries')
print('querying...')
conn = db.connect(db_name)
log_progress('SQL Connection initiated')
run_queries('SELECT * FROM Largest_banks',conn)
run_queries('SELECT AVG(MC_GBP_Billion) FROM Largest_banks',conn)
run_queries('SELECT Name from Largest_banks LIMIT 5',conn)
log_progress('Process Complete')
conn.close()
log_progress('Server Connection closed')





