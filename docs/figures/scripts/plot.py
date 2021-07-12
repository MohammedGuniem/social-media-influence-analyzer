import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('./datasets/social_media-ww-monthly-201001-201912-bar.csv')

columns=['Social Media', 'Percentage Market Share (Jan 2010 - Dec 2019)']

social_media_market_share = []

for index, row in df.iterrows():
    media = row['Social Media']
    market_share = row['Market Share Perc. (Jan 2010 - Dec 2019)']
    social_media_market_share.append((media, market_share))

df = pd.DataFrame(social_media_market_share, columns=columns)
mod_df = df[0:7]

others_df = pd.DataFrame([('Others', df[7:][columns[1]].sum())], columns=columns)

df = mod_df.append(others_df)
df = df[::-1]

fig, ax = plt.subplots()

df.plot.barh(x=columns[0], y=columns[1],  rot=0)


labels = []
for index, row in df.iterrows():
    media = row[columns[0]]
    market_share = row[columns[1]]
    labels.append(media + '  {:.2f}%'.format(market_share) )

plt.yticks(range(len(labels)), labels)
plt.tight_layout()
for spine in ax.spines.values():
    spine.set_visible(False)

ax.axes.get_xaxis().set_visible(False)
ax.tick_params(axis="y", left=False)
ax.invert_yaxis()

plt.savefig("../figures/most_popular_social_media_from_2010_to_2019.jpg")
