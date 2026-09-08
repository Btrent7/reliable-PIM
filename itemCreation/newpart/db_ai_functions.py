from rapidfuzz import fuzz
import pandas as pd
import sys

def normalize_text(text):
    if text is None:
        return ""
    return str(text).upper().strip()

def build_candidate_text(vendor_desc, vendor_sku, item_detail):
    # This mirrors the style of your Product name
    return f"{normalize_text(vendor_desc)},{normalize_text(vendor_sku)},{normalize_text(item_detail)}"

def score_similarity(new_text, existing_text):
    # token_set_ratio works well when words are similar but order changes
    return fuzz.token_set_ratio(new_text, normalize_text(existing_text))

def duplicate_check_fuzzy(dup_df, new_item_text, strong_threshold=90, review_threshold=30):
    if dup_df.empty:
        print("No duplicates found!")
        return True

    dup_df = dup_df.copy()

    dup_df["similarity_score"] = dup_df["item_name"].apply(
        lambda x: score_similarity(new_item_text, x)
    )

    dup_df = dup_df.sort_values("similarity_score", ascending=False)

    strong_matches = dup_df[dup_df["similarity_score"] >= strong_threshold]
    review_matches = dup_df[
        (dup_df["similarity_score"] >= review_threshold) &
        (dup_df["similarity_score"] < strong_threshold)
    ]

    if not strong_matches.empty:
        print("\nHIGH LIKELIHOOD DUPLICATE(S):\n")
        print(strong_matches[["item_number", "item_name", "similarity_score"]])

        while True:
            cont_boolean = input("Very likely duplicate found. Continue anyway? (Y/N): ").strip().upper()
            if cont_boolean in ("Y", "N"):
                return cont_boolean == "Y"
            print("Invalid input. Please enter 'Y' or 'N'.")

    if not review_matches.empty:
        print("\nPOSSIBLE DUPLICATE(S) TO REVIEW:\n")
        print(review_matches[["item_number", "item_name", "similarity_score"]])

        while True:
            cont_boolean = input("Possible duplicates found. Continue Part Number Creation? (Y/N): ").strip().upper()
            if cont_boolean in ("Y", "N"):
                return cont_boolean == "Y"
            print("Invalid input. Please enter 'Y' or 'N'.")

    print("No strong duplicates detected.")
    return True