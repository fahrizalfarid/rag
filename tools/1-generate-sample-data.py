import pandas as pd

df = pd.read_csv("law_qa.csv",sep=",")
df = df.head(1000)
id = [i for i in range(1000)]
df["join_text"] = df['question'] + '\n'+df['summarize']
pd.DataFrame({
    "id":id,
    "join_text":df["join_text"].tolist(),
}).to_csv("law_qa_1000_raw.csv",index=False,sep=",")
