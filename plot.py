from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from flask_cors import CORS
import urllib
from queue import Queue
from threading import Thread
import re

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

class ScrapingWorker(Thread):
    def __init__(self, queue, episode_data):
        Thread.__init__(self)
        self.queue = queue
        self.episode_data = episode_data

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            title_id, season = self.queue.get()
            try:
                episodes = scrape_episodes(title_id, season)
                self.episode_data.append(episodes)
            finally:
                self.queue.task_done()

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
                "rating": episode_rating,
                "season": season,
                "ep_number": episode_number,
                "total_votes": total_votes
            }

            episodes.append(episode_obj)
            episode_number += 1

    return episodes

@app.route('/list-episodes/<title_id>')
def get_title_episodes(title_id):
    # Getting how many seasons the title has
    page = urlopen(Request(
        url=f'https://www.imdb.com/title/{title_id}/?ref_=fn_al_tt_1', 
        headers={'User-Agent': 'Mozilla/5.0'}
    ))
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    seasons = soup.find(id='browse-episodes-season')
    seasons = seasons['aria-label']
    seasons = int(re.search("\d+", seasons).group())

    # Creating a queue that will store the title_id and season to be scraped
    queue = Queue()

    episode_data = []

    # Creating threads to run the queue
    for x in range(8):
        worker = ScrapingWorker(queue, episode_data)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Adding items to queue based on seasons and then waiting for them to end
    for season in range(1,seasons+1):
        queue.put((title_id, season))
    queue.join()

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