import os
import pandas as pd
import openpyxl as op
import psycopg
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

priceBook_list = (
    ROOT /
    "trade_agreement_templates" /
    "Cleaning Template.xlsx"
)


# Set Enviornment Variable in PowerShell:
# $env:DB_PASSWORD = "example-password"

print("USER:", os.getenv("DB_USER"))
print("PASSWORD EXISTS:", os.getenv("DB_PASSWORD") is not None)


# Connection parameters
conn = psycopg.connect(
    host="aws-1-us-east-2.pooler.supabase.com",
    port=5432,
    dbname="postgres",
    user= os.getenv('DB_USER'),          # Use Environment Variable
    password= os.getenv('DB_PASSWORD'),  # Use Environment Variable
    sslmode="require"
)


sql = """
SELECT DISTINCT
  "item_number" AS "Item number",
  "primary_vendor" AS "Vendor",
  "legal_entity"
FROM "pbi_item_master"
ORDER BY "legal_entity", "item_number";
"""

itemMaster = pd.read_sql(sql, conn)

# print(itemMaster)


clean_pb_list = pd.DataFrame(pd.read_excel(priceBook_list, sheet_name='CLEAN'))
clean_pb_list['Item number'] = clean_pb_list['Item number'].astype(str)

pb_items = pd.merge(clean_pb_list, itemMaster, on='Item number', how='inner').sort_values(by='legal_entity').reset_index()
pb_items = pb_items.drop(columns=['index'])

# Drop unnamed columns only if they exist
pb_items = pb_items.drop(columns=['Unnamed: 3', 'Unnamed: 4'], errors='ignore')

pb_items['TPP'] = pb_items['TPP'].round(4)
pb_items['LIST'] = pb_items['LIST'].round(2)

pb_items = pb_items.replace('nan', '')



print(pb_items)

with pd.ExcelWriter(priceBook_list, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    pb_items.to_excel(writer, sheet_name='test', index=False)



# INPUT FUNCTION FOR LATER UPGRADES:

# required_le = pb_items[pb_items['LEGALENTITY'].isin(legal_entities)]

# items_by_entity = (required_le.groupby('LEGALENTITY')['Item number'].apply(list))

# for le, items in items_by_entity.items():
#     print(f"LEGALENTIY {le}")
#     print(items)
