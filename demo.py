# ------------------------------------------------------
# CDS Web Scraping Workshop
# by Tushar Khan
# adapted by Bryant Park
#
# Created: February 29, 2020
# Last Modified: October 23, 2021 (by Tushar)
# Forked: February 21, 2023
# ------------------------------------------------------

import requests, pandas as pd
from bs4 import BeautifulSoup

# Create dataframe
features = ['post score', 'comment score', 'post link', 'commenter', 'comment']
df = pd.DataFrame(columns=features)

# Request top posts page
base_url   = 'https://old.reddit.com/r/Cornell/top/'
user_agent = {'User-Agent': 'Mozilla/5.0'}

r = requests.get(base_url, params={'t': 'all', 'limit': 5}, headers=user_agent)

# Extract comment section links from the page
soup = BeautifulSoup(r.text, 'lxml')
link_tags = soup.find_all('a', class_='bylink comments may-blank')

links = [tag['href'] for tag in link_tags]

# Iterate over the links
for i, link in enumerate(links):
    print(f'Scraping data from post {i+1} of {len(links)}')

    r = requests.get(link, params={'sort': 'top'}, headers=user_agent)
    soup = BeautifulSoup(r.text, 'lxml')

    # Extract original post score
    score_str = soup.find('div', class_='linkinfo').find('span', class_='number').text
    op_score = int(score_str.replace(',', '')) # because `find` returns a string

    # Extract the comments from the comment section
    comment_filter = lambda t: t.find('span', class_='score unvoted') is not None
    comments = soup.find_all(comment_filter, attrs={'class': 'entry unvoted'})

    # Iterate over the comments
    for container in comments:

        # Extract commenter - could be blank
        commenter_tag = container.find(class_='author')
        commenter = commenter_tag.text if commenter_tag is not None else '[deleted]'

        # Extract comment text and score
        comment = container.find('div', class_='usertext-body').text.strip().replace('\n', ' ')
        score = int(container.find(class_='score unvoted')['title'])

        # Append data to dataframe
        df.loc[len(df.index)] = [op_score, score, link, commenter, comment]

# Write dataframe to csv
df.to_csv('reddit_comments.csv', index=False)

# Inspect dataset
print(df.sort_values(by='comment score', ascending=False).head())