import psycopg
import pandas as pd

# Connection parameters
conn = psycopg.connect(
    host="aws-1-us-east-2.pooler.supabase.com",
    port=5432,
    dbname="postgres",
    user="postgres.PROJECT-CODE",
    password="PASSWORD",
    sslmode="require"
)


sql = """
SELECT
  "Item number",
  "Product name"
FROM "Item_Master"
ORDER BY "Item number";
"""

df = pd.read_sql(sql, conn)

print(df)

conn.close()
