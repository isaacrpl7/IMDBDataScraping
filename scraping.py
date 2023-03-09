from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

tv_series = input("Digite o nome de uma série\n")
page = urlopen(Request(
    url=f'https://www.imdb.com/find/?q={tv_series}&ref_=nv_sr_sm', 
    headers={'User-Agent': 'Mozilla/5.0'}
))
html = page.read().decode("utf-8")

soup = BeautifulSoup(html, "html.parser")
section = soup.find(attrs={"data-testid": "find-results-section-title"})
div_list = section.contents[1]
ul = div_list.contents[0]
items = ul.contents

k=1
for item in items:
    print(f'---------- {k} ----------')

    title = item.find('a')
    title_string = title.string
    href = title['href']
    title_id = href.split('/')[2]

    print(f'Title: {title_string}')
    print(f'Id: {title_id}')

    for li in item.find_all('li'):
        print(li.string)
    k += 1

    print("")

number = input("Digite o número referente à série que você quer analisar:\n")
series_id = items[int(number)-1].find('a')['href'].split('/')[2]

print(f'Id: {series_id}')

# Página dos episódios
next_season = True
season = 1
episode_data = []
while(next_season):
    page = urlopen(Request(
        url=f'https://www.imdb.com/title/{series_id}/episodes?season={season}', 
        headers={'User-Agent': 'Mozilla/5.0'}
    ))
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    episode_list = soup.find_all(class_="list_item")

    episode_number = 1
    for episode in episode_list:
        # Getting each episode the 'a' tag
        strong = episode.find("strong")
        link = strong.find("a")

        episode_url = link['href']
        episode_name = link.string

        episode_rating = episode.find(class_="ipl-rating-star__rating").string
        print(f'Episode name: {episode_name}')
        print(f'Episode rating: {episode_rating}')
        print(f'Season: {season}')
        print(f'Episode number: {episode_number}')
        print("")
        episode_obj = {
            "name": episode_name,
            "rating": episode_rating,
            "season": season,
            "ep_number": episode_number
        }

        episode_data.append(episode_obj)

        episode_number += 1

    # Tem mais temporadas?
    next_season = True if soup.find(id="load_next_episodes") != None else False
    season += 1