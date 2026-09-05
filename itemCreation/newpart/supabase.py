## ------------------------------------------------------------------------------------ ##
## --------------------------------------- CONFIG ------------------------------------- ##
## ------------------------------------------------------------------------------------ ##
from hashlib import new

import openpyxl as op
import pandas as pd

import warnings
from datetime import date
import sys

import os
import psycopg  # psycopg v3
from . import db_functions as db
from . import db_ai_functions as ai


# Remove SQL Warning Prints
warnings.filterwarnings("ignore", category=UserWarning)


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




## ------------------------------------------------------------------------------------ ##
## -------------------------- READ & FORMAT FORM INPUTS ------------------------------- ##
## ------------------------------------------------------------------------------------ ##

# Connect to Excel Templates
newPart_form  = r"newpart\excel_files\NewPartNumber_Form.xlsx"
newPart_table = r"newpart\excel_files\NewPartNumber_Table.xlsx"


# Open Excel read _form
wb_form = op.load_workbook(newPart_form)
form = wb_form["newPart"]


# Format imputs
vendor_desc = form["B2"].value.strip()
vendor_id   = form["B3"].value.upper().strip()
vendor_sku  = str(form["B4"].value).strip().upper()
item_detail = form["B5"].value.strip()
item_weight = form["B6"].value
item_depth  = form["B7"].value
item_height = form["B8"].value
item_width  = form["B9"].value
item_purch  = float(form["B10"].value)
search      = form["B11"].value
location    = form["B12"].value.upper()
request     = form["B13"].value
item_prdGrp = form["B14"].value
time_stamp  = date.today()


# Legal Entity Assignment
valid_entities = (10, 30, 31, 36, 37, 38, 40, 46, 47, 50)
while True:
    legalEntity = int(input('Legal Entity: '))
    
    if legalEntity in valid_entities:
        break
    else:
        print("Invalid Legal Entity. Try again.")


# Build item description (your original script formats ITMDESC; keep your real logic here)
item_descript = db.item_description(vendor_desc, vendor_sku, item_detail)





## ------------------------------------------------------------------------------------ ##
## --------------------------------- DUPLICATE CHECK ---------------------------------- ##
## ------------------------------------------------------------------------------------ ##

# Check Supabase for Duplicate Vendor SKU
sku_param = f"%#{vendor_sku},%"
le_param     = f"{legalEntity}"


# Duplicate Check SQL Query
sql = """
SELECT
  "Item number",
  "Product name"
FROM "Item_Master"
WHERE "Product name" LIKE %s
    AND "LEGALENTITY" = %s
    AND "Product name" NOT ILIKE %s
ORDER BY "Item number";
"""


# MANUALLY Read Duplicate SQL Query as DataFrame
dup_df  = pd.DataFrame(pd.read_sql(sql, conn, params=[sku_param, le_param, '%#NONE%'])) # remove item with error description: #NONE 

# Decision: If list contains values, print dup_list, else print input(Y/N)
if not db.duplicate_check(dup_df):
    sys.exit(1)



# FUZZY Matching for Duplicate Check
new_item_check = ai.build_candidate_text(vendor_desc, vendor_sku, item_detail)

# Decision: If list contains values, print dup_list, else print input(Y/N)
if not ai.duplicate_check_fuzzy(dup_df, new_item_check):
    sys.exit(1)





## ------------------------------------------------------------------------------------ ##
## ------------------------------- ITEM CONFIGURATION --------------------------------- ##
## ------------------------------------------------------------------------------------ ##

# Check Supabase for category description and like-item
template_df, template_le_used = db.get_template_item(conn, search, vendor_id, legalEntity)

if template_df.empty:
    print(f"No like-item found in LE{legalEntity} or fallback LE10.")
    purchLinedisc = input("Manually Add Discount Group: ").strip()
else:
    purchLinedisc = str(template_df["PurchLineDiscount"].iloc[0]).strip() or input("Manually Add Discount Group: ").strip()


# Check for Purchase Line Discount Automation
if not template_df.empty and 'PurchLineDiscount' in template_df.columns:
    purchLinedisc = str(template_df['PurchLineDiscount'].iloc[0]).strip()
else:
    purchLinedisc = str(input('Manually Add Discount Group: '))


# Pass Discount Group for List Price calculation
list_price = db.markup(purchLinedisc, item_purch)


# Extract Template Item Data
temp_itemNumb = template_df["Item number"].iloc[0]
temp_itemDesc = template_df["Product name"].iloc[0]
temp_vendor   = db.get_vendor_by_entity(conn, vendor_id, legalEntity)
temp_img      = template_df["Item model group"].iloc[0]
temp_itemGrp  = template_df["Item group"].iloc[0]
temp_prodGrp  = template_df["Production group"].iloc[0]
temp_purchTax = template_df["PurchTax"].iloc[0]
temp_purchUOM = template_df["PurchUOM"].iloc[0]
temp_coo      = template_df["Country/region"].iloc[0]
temp_prodtyp  = template_df["Production type"].iloc[0]
temp_property = template_df["Property"].iloc[0]
temp_saleUnit = template_df["SalesUnit"].iloc[0]
temp_salesTax = template_df["SalesTax"].iloc[0]
temp_prodPool = "MTO"
temp_covrgGrp = ""
temp_prodlyf  = "70 - Saleable"
temp_priceBk  = "No"
temp_legalEnt = legalEntity





## ------------------------------------------------------------------------------------ ##
## ------------------------- UPLOAD NEW ITEM TO DATABASE ------------------------------ ##
## ------------------------------------------------------------------------------------ ##









## ------------------------------------------------------------------------------------ ##
## ----------------------------- PRINT DATA FOR USER ---------------------------------- ##
## ------------------------------------------------------------------------------------ ##


# SQL function for New Part Number generator
new_part_number = db.generate_699_part_number(conn)

# TableKey
tableKey = str(new_part_number) + '-' + str(legalEntity) # Change temp_itemNumb to New Item Number

print(f'''
Template Item:
{temp_itemNumb}  :  {temp_itemDesc}   |   {purchLinedisc}   |   {temp_property}

-- Email Response --

New Item:
Item Number:  {new_part_number} 
Item Descpt:  {item_descript}
Vendor SKU:   {vendor_sku}
Vendor ID:    {vendor_id} | {temp_vendor}

Location:     {location}
Notes:        {request}

Purch Price:  {item_purch}
List Price:   {list_price}
Created On:   {time_stamp}

Thanks,
''')