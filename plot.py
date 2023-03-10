from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from flask_cors import CORS
import urllib

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

@app.route('/list-episodes/<title_id>')
def get_title_episodes(title_id):
    next_season = True
    season = 1
    episode_data = []
    while(next_season):
        page = urlopen(Request(
            url=f'https://www.imdb.com/title/{title_id}/episodes?season={season}', 
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

                episode_data.append(episode_obj)

                episode_number += 1

        # Tem mais temporadas?
        next_season = True if soup.find(id="load_next_episodes") != None else False
        season += 1

    return jsonify(episode_data)

if __name__ == '__main__':
    app.run()