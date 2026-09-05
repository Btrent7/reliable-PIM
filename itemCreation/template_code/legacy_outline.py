import openpyxl as op
from .listPrice import markup
from datetime import date
import sys
# import pyodbc
import pandas as pd

# Excel File Path
dcscim = r"C:\Users\New Part Number\DCSCIM.xlsx"
newPart_form = r"C:\Users\New Part Number\NewPartNumber_Form.xlsx"
newPart_table = r"C:\Users\New Part Number\NewPartNumber_Table.xlsx"


# Load Form Workbook (openpyxl)
wb_form = op.load_workbook(newPart_form)
form = wb_form["newPart"]


# Part Number Variables Defined
vnd_name  = form["B2"].value.strip()
vnd_id    = form["B3"].value.upper().strip()
sku       = str(form["B4"].value).strip()
detail    = form["B5"].value.strip()
tpp       = float(form["B10"].value)
cat_desc  = form["B11"].value
site      = form["B12"].value.upper()
request   = form["B13"].value
prod_grp  = form["B14"].value


# Dupliacate Test Query
cim_table = pd.read_excel(dcscim, sheet_name='DCSCIM')
cim_table = pd.DataFrame(cim_table)


# Dupliacate Test Query
dup_query = cim_table.query("ITMDESC.str.contains(@sku)")


# Build a list of duplicate ITMID
dup_list = (
    dup_query["ITMID"]
    .dropna()
    .astype(str)        # ensure string type
    .str.strip()        # remove whitespace
    .str.zfill(10)      # left-pad to 10 digits if needed
    .tolist()
)


# Stop if duplicates were found, else continue
if dup_list:
    print(f"""
          {dup_query}

          Duplicate part(s) detected: 
          {dup_list}""")
    sys.exit(1)  # or 'return' if you're inside a function
else:
    print("""
          No duplicates found!
          """)

## --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ##
# For Items already in the system, STOP script. Otherwise continue...
## --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ##


# Product Category Query
vnd_query = cim_table.query("VNDID.str.contains(@vnd_id, na=False)")
prd_query = vnd_query.query("ITMDESC.str.contains(@cat_desc, na=False)")
prd_query = prd_query.groupby('PRDCTG').count().sort_values(by='ITMID', ascending=False).reset_index()

prd_value = prd_query['PRDCTG'].loc[0]

print(prd_value)


# Product Template Query
temp_query = cim_table.query("VNDID.str.contains(@vnd_id, na=False)")
temp_query = temp_query.query("PRDCTG.str.contains(@prd_value, na=False)")
temp_query = temp_query.query("ITMDESC.str.contains(@cat_desc, na=False)").reset_index()

temp_query = temp_query['ITMID'].loc[0]

print(temp_query)


print(f'''
Template Item:
{prd_value}''')
print(temp_query)


# Creation Date
today = date.today()


# Item Description
item_descr = (f"{vnd_name},#{sku},{detail}").upper()


# List Price Function
list_price = markup(prd_value, tpp)

if list_price is None:
    sys.exit()
else:
    print(f"""
Form accessed, markup applied: {today}""")


# Load Table Workbook (openpyxl)
wb_table = op.load_workbook(newPart_table)
table = wb_table["699_Table"]


# Select Next Blank Row in Table
next_row = 1
while table.cell(row=next_row, column=1).value is not None:
    next_row += 1


# Select Previous Row (for previous part number)
prev_pn_cell = table.cell(row= next_row - 1, column= 1).value
previous_pn = int(prev_pn_cell)


# Create New Part Number
new_pn = previous_pn + 1


# Fill Next Blank Row on Table
table.cell(row = next_row, column = 1,  value = new_pn)
table.cell(row = next_row, column = 2,  value = sku)
table.cell(row = next_row, column = 3,  value = item_descr)
table.cell(row = next_row, column = 4,  value = today)
table.cell(row = next_row, column = 5,  value = site)
table.cell(row = next_row, column = 6,  value = tpp)
table.cell(row = next_row, column = 7,  value = prd_value)
table.cell(row = next_row, column = 11, value = list_price)
table.cell(row = next_row, column = 12, value = vnd_id)

wb_table.save(newPart_table)
wb_table.close()


# Print in Terminal for Data Entry & Email Script
print(f"""
Done!     

New PN:   {new_pn}
VNDID:    {vnd_id}
Item:     {item_descr}
TPP:      {tpp}
List:     {list_price}
Request:  {request}
Site:     {site}

Prod Grp: {prod_grp}

Thanks, 
""")
