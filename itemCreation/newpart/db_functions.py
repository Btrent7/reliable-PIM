import pandas as pd


# GENERATE LIST PRICE FOR supabase.py
# Map each category_code to its divisor
markup_dict = {
    "257A": 0.240, "257B": 0.240, "257C": 0.240, "257F": 0.240, "257G": 0.240, "257H": 0.240, "343B": 0.256,
    "442A": 0.196, "444A": 0.280, "450A": 0.224, "465A": 0.216, "500A": 0.400, "500B": 0.240, "500C": 0.240,
    "501A": 0.059, "501B": 0.059, "501C": 0.059, "501D": 0.068, "501E": 0.136, "501F": 0.070, "501G": 0.070,
    "501H": 0.070, "501I": 0.052, "502A": 0.134, "502B": 0.134, "502C": 0.134, "502D": 0.134, "502E": 0.134,
    "502G": 0.080, "502H": 0.080, "502I": 0.080, "502J": 0.080, "502K": 0.144, "502L": 0.144, "502M": 0.400,
    "502N": 0.132, "502P": 0.128, "502Q": 0.132, "502R": 0.132, "502S": 0.072, "502T": 0.072, "502U": 0.072,
    "503A": 0.076, "503B": 0.076, "503C": 0.076, "503D": 0.076, "503E": 0.076, "503F": 0.076, "503G": 0.068,
    "503H": 0.068, "503I": 0.068, "503K": 0.132, "503L": 0.148, "503M": 0.148, "503S": 0.148, "504A": 0.144,
    "504B": 0.144, "504C": 0.144, "504D": 0.144, "504E": 0.144, "504F": 0.144, "504G": 0.144, "504H": 0.144,
    "504I": 0.144, "505A": 0.124, "505B": 0.124, "505C": 0.124, "505D": 0.124, "505E": 0.124, "505F": 0.124,
    "505G": 0.124, "505H": 0.124, "505I": 0.124, "506A": 0.176, "506B": 0.176, "506M": 0.352, "507A": 0.208,
    "507B": 0.228, "507C": 0.248, "508A": 0.184, "509A": 0.240, "509B": 0.240, "509C": 0.240, "509D": 0.272,
    "510A": 0.212, "510D": 0.212, "510Z": 0.216, "511A": 0.158, "511B": 0.140, "511C": 0.080, "511D": 0.148,
    "511E": 0.148, "511H": 0.068, "511I": 0.240, "511J": 0.152, "511K": 0.224, "511L": 0.160, "511M": 0.140,
    "511T": 0.196, "511Y": 0.158, "513A": 0.220, "513B": 0.220, "513C": 0.220, "513D": 0.220, "513E": 0.220,
    "513F": 0.220, "514A": 0.108, "515A": 0.100, "515B": 0.100, "515C": 0.240, "518A": 0.224, "519A": 0.320,
    "519B": 0.320, "519C": 0.320, "519D": 0.320, "536A": 0.208,
}
#Markup Item Function
def markup(category_code, tpp_value):
    var = 1.5
    try:
        divisor = markup_dict[category_code]
        tpp_value = float(tpp_value)
        list_price = round((var * tpp_value) / divisor, 2)
        return list_price
    except KeyError:
        print(f"Undefined Item Category: '{category_code}'")
        return None
    except (ValueError, TypeError):
        print("Invalid TPP value.")
        return None
    except Exception as e:
        print("❌ ERROR:", e)
        print("❌ TYPE:", type(e))
        return None




# GENERATE NEW PART NUMBERS FOR supabase.py
def generate_699_part_number(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT public.generate_699_part_number();")
            result = cur.fetchone()

        # Important: commit the transaction so the increment persists
        conn.commit()

        return result[0]

    except Exception as e:
        conn.rollback()
        print(f"Error generating part number: {e}")
        raise




# RESET 699 PART NUMBER FOR reset699.py
def set_699_part_number(conn, new_num):
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT public.set_part_number_counter(%s, %s);",
                ('699', new_num)
            )

        conn.commit()

        with conn.cursor() as cur:
            cur.execute(
                "SELECT next_value FROM public.part_number_counter WHERE series = %s;",
                ('699',)
            )
            result = cur.fetchone()

        return result[0]

    except Exception as e:
        conn.rollback()
        print(f"Error setting new part number: {e}")
        raise




# GET TEMPLATE FROM supabase.py
def get_template_item(conn, search, vendor_id, legal_entity, fallback_entity='0010'):
    search_param = f"%{search}%"
    vnd_param = str(vendor_id)

    # ✅ Validate vendor_id against both columns
    vendor_check_sql = """
    SELECT
        CASE
            WHEN EXISTS (
                SELECT 1
                FROM pbi_item_master
                WHERE vendor_search_name = %s
            ) THEN 'vendor_search_name'

            WHEN EXISTS (
                SELECT 1
                FROM pbi_item_master
                WHERE primary_vendor = %s
            ) THEN 'primary_vendor'
        ELSE NULL
    END AS match_column;
    """

    vendor_match = pd.read_sql(vendor_check_sql, conn, params=[vnd_param, vnd_param])

    match_column = vendor_match.iloc[0]["match_column"]

    if match_column is None:
        raise ValueError(f"Invalid vendor_id: {vendor_id} not found in either column")

    # ✅ Main query
    sql_template_item = f"""
    WITH Items AS(
        SELECT
            "item_number",
            "item_name"
        FROM pbi_item_master
        WHERE "item_name" LIKE %s   
            AND "{match_column}" = %s
            AND "legal_entity" = %s
    )

    SELECT 
        *
    FROM Items
    LIMIT 1;
    """

    # Try requested entity
    df = pd.read_sql(sql_template_item, conn, params=[search_param, vnd_param, legal_entity])

    # Fallback logic
    if df.empty and legal_entity != fallback_entity:
        df = pd.read_sql(sql_template_item, conn, params=[search_param, vnd_param, fallback_entity])
        return df, fallback_entity

    return df, legal_entity




# FIND VENDOR FOR DESIRED LEGAL ENTITY IN supabase.py
def get_vendor_by_entity(conn, vendor_id, legal_entity, fallback_vendor="V0010"):
    """
    Returns the corresponding matching value from the opposite column
    within the specified legal entity.
    """

    vendor_id = str(vendor_id).strip()

    sql = """
        SELECT
            vendor_search_name,
            primary_vendor
        FROM pbi_item_master
        WHERE legal_entity = %s
          AND (
                vendor_search_name = %s
                OR primary_vendor = %s
              )
        LIMIT 1;
    """

    df = pd.read_sql(
        sql,
        conn,
        params=[legal_entity, vendor_id, vendor_id]
    )

    if df.empty:
        return fallback_vendor

    vendor_search_name = str(df.iloc[0]["vendor_search_name"]).strip()
    primary_vendor = str(df.iloc[0]["primary_vendor"]).strip()

    # If user supplied vendor_search_name, return primary_vendor
    if vendor_id == vendor_search_name:
        return primary_vendor

    # If user supplied primary_vendor, return vendor_search_name
    if vendor_id == primary_vendor:
        return vendor_search_name

    return fallback_vendor



# REFACOTR ITEM DESC BASED ON VENDOR SKU supabase.py
def item_description(vendor_desc, vendor_sku, item_detail):
    invalid_skus = {'0', None, 'N/A', '', 'NONE'}
    
    if vendor_sku in invalid_skus:
        return f"{vendor_desc},{item_detail}".upper()
    
    return f"{vendor_desc},#{vendor_sku},{item_detail}".upper()




# DECISION: If list contains values, print dup_list, else print input(Y/N)
def duplicate_check(dup_df):
    if dup_df.empty:
        print("No duplicates found!")
        return True

    dup_list = (
        dup_df["item_number"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.zfill(10)
        .tolist()
    )

    print("\nDuplicate part(s) detected:\n")
    print(dup_df)
    print("\nItem Numbers:", dup_list)

    while True:
        cont_boolean = input("Continue Part Number Creation? (Y/N): ").strip().upper()
        if cont_boolean in ('Y', 'N'):
            return cont_boolean == 'Y'
        print("Invalid input. Please enter 'Y' or 'N'.")