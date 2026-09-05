import os
import psycopg  # psycopg v3
from . import db_functions as db


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



new_item = int(input('New Item: '))

db.set_699_part_number(conn, new_item)
