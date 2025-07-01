import pandas as pd
coord_df = pd.read_csv("sector_coords.csv")
sector_coords = {row["Sector"]: [row["Latitude"], row["Longitude"]] for _, row in coord_df.iterrows()}
print(sector_coords["Sector 1"])  # Output: [18.7002, 82.8608]
