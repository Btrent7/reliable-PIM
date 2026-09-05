import pandas as pd
import openpyxl as op

file = r'C:\Users\btrent\OneDrive - The Reliable Automatic Sprinkler Co., Inc\Data Analysis\New Part Number\Dynamics\ItemMaster.xlsx'
upload = r'C:\Users\btrent\OneDrive - The Reliable Automatic Sprinkler Co., Inc\Data Analysis\New Part Number\Dynamics\itemMasterUpload.xlsx'

itemMaster = pd.DataFrame(pd.read_excel(file, sheet_name='Dynamics'), dtype=str)
dVend = pd.DataFrame(pd.read_excel(file, sheet_name='D365 Vendor'), dtype=str)
aVend = pd.DataFrame(pd.read_excel(file, sheet_name='ASI Vendor'), dtype=str)
vendorKey = pd.DataFrame(pd.read_excel(file, sheet_name='Vendor'), dtype=str)


merge = pd.merge(itemMaster, vendorKey, how='left', on=['LEGALENTITY', 'Vendor'])

merge = merge.replace('nan', '')
print(merge)

# with pd.ExcelWriter(upload, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer: 
#     merge.to_excel(writer, sheet_name='Upload', index=False)