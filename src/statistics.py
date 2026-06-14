import pandas as pd

df = pd.read_csv("data/cities.csv")

print("Number of cities:", len(df))

print("\nCities per country:")
print(df["country"].value_counts().head(10))
