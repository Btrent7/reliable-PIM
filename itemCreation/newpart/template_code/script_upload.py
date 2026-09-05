import psycopg
import pandas as pd

# Connection parameters
conn = psycopg.connect(
    host="aws-1-us-east-2.pooler.supabase.com",
    port=5432,
    dbname="postgres",
    user="DB_USER_VALUE",
    password="PASSWORD",
    sslmode="require"
)



created_by = os.environ.get("USERNAME", "unknown")

# ---------- ALLOCATE + INSERT ATOMICALLY ----------
with psycopg.connect(conn) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT allocate_part_number(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
            (
                SERIES,
                vnd_id,
                sku,
                detail,
                item_descr,
                site,
                tpp,
                cat_code,
                list_price,
                request,
                prod_grp,
                created_by
            )
        )
        new_pn = cur.fetchone()[0]
    conn.commit()


print("Done!")