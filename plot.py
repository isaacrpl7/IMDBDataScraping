from gevent import monkey
monkey.patch_all()
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from flask_cors import CORS
import urllib
import re
import gevent
import time

app = Flask(__name__)
CORS(app)

@app.route('/search')
def get_scraped_data():
    searchword = request.args.get('serie', '')
    searchurl = urllib.parse.quote(searchword)

    page = urlopen(Request(
        url=f'https://www.imdb.com/find/?q={searchurl}&ref_=nv_sr_sm', 
        headers={'User-Agent': 'Mozilla/5.0'}
    ))
    html = page.read().decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")
    section = soup.find(attrs={"data-testid": "find-results-section-title"})
    div_list = section.contents[1]
    ul = div_list.contents[0]
    items = ul.contents

    results = []

    k=1
    for item in items:
        print(f'---------- {k} ----------')

        title = item.find('a')
        title_string = title.string
        href = title['href']
        title_id = href.split('/')[2]

        print(f'Title: {title_string}')
        print(f'Id: {title_id}')

        description = []
        for li in item.find_all('li'):
            print(li.string)
            description.append(li.string)
        k += 1

        results.append({
            "title": title_string,
            "description": description,
            "title_id": title_id
        })

        print("")

    return jsonify(results)

class ScrapingWorker(gevent.Greenlet):
    def __init__(self, season, title_id, episode_data):
        gevent.Greenlet.__init__(self)
        self.season = season
        self.title_id = title_id
        self.episode_data = episode_data

    def _run(self):
        episodes = scrape_episodes(self.title_id, self.season)
        self.episode_data.append(episodes)

def scrape_episodes(title_id, season):
    page = urlopen(Request(
        url=f'https://www.imdb.com/title/{title_id}/episodes?season={season}', 
        headers={'User-Agent': 'Mozilla/5.0'}
    ))
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    episode_list = soup.find_all(class_="list_item")

    episodes = []
    episode_number = 1
    for episode in episode_list:
        # Getting each episode the 'a' tag
        strong = episode.find("strong")
        link = strong.find("a")

        episode_url = link['href']
        episode_name = link.string

        episode_rating = episode.find(class_="ipl-rating-star__rating")
        total_votes = episode.find(class_="ipl-rating-star__total-votes")
        if episode_rating != None and total_votes != None:
            episode_rating = episode_rating.string
            total_votes = total_votes.string.strip('()')

            print(f'Episode name: {episode_name}')
            print(f'Episode rating: {episode_rating}')
            print(f'Season: {season}')
            print(f'Episode number: {episode_number}')
            print(f'Total votes: {total_votes}')
            print("")
            episode_obj = {
                "name": episode_name,
                "rating": float(episode_rating),
                "season": season,
                "ep_number": episode_number,
                "total_votes": int(total_votes.replace(',', ''))
            }

            episodes.append(episode_obj)
            episode_number += 1

    return episodes

@app.route('/list-episodes/<title_id>')
def get_title_episodes(title_id):
    # Retrieving how many seasons the title has
    page = urlopen(Request(
        url=f'https://www.imdb.com/title/{title_id}/?ref_=fn_al_tt_1', 
        headers={'User-Agent': 'Mozilla/5.0'}
    ))
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    seasons = soup.find(id='browse-episodes-season')
    if seasons == None:
        seasons = soup.find(attrs={"data-testid": "episodes-browse-episodes"})
        seasons = seasons.find(string=re.compile("season", re.IGNORECASE))
    else:
        seasons = seasons['aria-label']
    seasons = int(re.search("\d+", seasons).group())

    episode_data = []

    threads = []
    start = time.time()
    for season in range(1, seasons+1):
        t = ScrapingWorker(season, title_id, episode_data)
        threads.append(t)
    for t in threads:
        t.start()
    gevent.joinall(threads)
    end = time.time()
    print("Tempo decorrido (segundos):")
    print(end-start)

    for index, season in enumerate(episode_data):
        if len(season) == 0:
            del episode_data[index]

    # Sorting the result by season
    def sortFunc(season):
        return season[0]['season']
    if len(episode_data) > 1:
        episode_data.sort(key=sortFunc)

    # Flattening the matrix to an array
    flat_episode_data_list = []
    for sublist in episode_data:
        for item in sublist:
            flat_episode_data_list.append(item)

    return jsonify(flat_episode_data_list)

if __name__ == '__main__':
    app.run()