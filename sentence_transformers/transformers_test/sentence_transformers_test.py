import pandas as pd
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer(
    r".\sentence_transformers\Config Files",
    local_files_only=True
)

ascfile = r'itemMaster\ASC Volumetrics.xlsx'
ascCatalogue = pd.DataFrame(pd.read_excel(ascfile, sheet_name='match'), dtype=str)

test_item = 'ASC 0890216220 7089 3" DI-ELECTRIC NIPPLE GXG' # 6990031051

embedding_itemMaster = model.encode(ascCatalogue['desc_match'].tolist())
embedding_newItem    = model.encode(test_item)

print('Encoded Complete!')

scores = util.cos_sim(embedding_itemMaster, embedding_newItem)

print('Scores Complete!')

# Flatten scores from shape [n, 1] to [n]
scores = scores.squeeze()

# Get top 3 highest scores
top_results = scores.topk(k=10)

print("Top 3 Matches:")

for score, idx in zip(top_results.values, top_results.indices):
    item = ascCatalogue['desc_match'].iloc[idx.item()]
    percent = round(score.item() * 100, 2)
    print(f"{percent}% - {item}")

print('Code Finished.')





# TEST SEQUENCE:

# itemMaster = [
#     'ANVIL,#7088,2" PLASTIC SCREW',
#     'RASCO,#1800,3" PLASTIC BOLT',
#     'ASC,#1700,4" PLASTIC NUT'
# ]
# newItem = 'ASC,#0123456789,2" HYDRO PLASTIC SCREW'

# embedding_itemMaster = model.encode(itemMaster)
# embedding_newItem    = model.encode(newItem)

# scores = util.cos_sim(embedding_itemMaster, embedding_newItem)

# print(embedding_itemMaster)
# print(embedding_newItem)

# print(scores)
