import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('./datasets/social_media-ww-monthly-201101-202012.csv')
df[['Year','Month']] = df.Date.str.split("-", expand=True)
df = df.groupby(['Year']).sum()

fig, ax = plt.subplots()
df_sum = ((df.sum(numeric_only=True, axis=0)/120).round(2))
print(df_sum.sort_values(ascending=False))

medias = ['Facebook', 'Pinterest', 'Twitter', 'StumbleUpon', 'YouTube', 'reddit', 'Tumblr', 'Instagram', 'VKontakte', 'LinkedIn', 'Google+']

(df_sum[medias]).plot(kind="barh")

labels = []
for media in medias:
    labels.append(media + '  {:.2f}%'.format(df_sum[media]) )

plt.yticks(range(len(labels)), labels)
plt.tight_layout()
for spine in ax.spines.values():
    spine.set_visible(False)

ax.axes.get_xaxis().set_visible(False)
ax.tick_params(axis="y", left=False)
ax.invert_yaxis()

plt.savefig("../figures/most_popular_social_media_from_2011_to_2020.jpg")
