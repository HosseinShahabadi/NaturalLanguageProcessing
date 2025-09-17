import pandas as pd


df = pd.read_csv("./Pairs/Texts.csv")

df = df[["id", "text"]]
df = df.rename(columns={"text": "summary"})

df.to_json("./Pairs/Texts.json", orient="records", force_ascii=False, indent=4)
