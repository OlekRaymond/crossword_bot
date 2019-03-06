import pickle
from collections import namedtuple, defaultdict
from random import choice
import requests

from bs4 import BeautifulSoup
import markovify
from twython import Twython

Clue = namedtuple('Clue', 'setter xword_id clue_number raw_clue words pattern')
Setter = namedtuple('Setter', 'name clues markov')

credentials = {'app_key': 'your',
               'app_secret': 'details',
               'oauth_token': 'go',
               'oauth_token_secret': 'here'}

twitter_handles = {'Qaos': '@qaos_xword',
                   'Boatman': '@BoatmanCryptics',
                   'Hectence': '@Hectence',
                   'Navy': '@navy_clues',
                   'Paul': '@crosswordpaul',
                   'Tramp': '@Tramp_crossword',
                   'Enigmatist': '@enigmatistelgar'}


def get_crossword_id():
    url = 'https://www.theguardian.com/crosswords/series/cryptic'
    p = requests.get(url)
    soup = BeautifulSoup(p.content, 'html.parser')
    return int(soup.find(class_='fc-item')['data-id'].split('/')[-1])


def scrape_clues(crossword_id):
    base = 'https://www.theguardian.com/crosswords/cryptic/'
    p = requests.get(base + str(crossword_id))
    soup = BeautifulSoup(p.content, 'html.parser')
    setter = soup.find(class_='byline').find('a').text
    clues = soup.find(class_='crossword__clues')
    todays_clues = []
    for clue in clues.findAll('li'):
        clue_number, raw_clue = (c.text for c in clue.findAll('div'))
        *words, pattern = raw_clue.split()
        for i, word in enumerate(words):  # Strip the punctuation
            words[i] = ''.join([char for char in word if char.isalpha()
                                or char == '-'])
        words = [w for w in words if w and w != '-']
        todays_clues.append(Clue(setter, crossword_id, clue_number,
                                 raw_clue, words, pattern))
    return todays_clues


def make_tweet(setter, crossword_id, clue):
    url = 'https://www.theguardian.com/crosswords/cryptic/' + str(crossword_id)
    if setter in twitter_handles.keys():
        setter = twitter_handles[setter]
    openings = [f"Today's @guardian crytpic crossword set by {setter}. ",
                f"Thanks to {setter} for today's @guardian cryptic. ",
                f"{setter} sets the @guardian cryptic today. "]
    middles = [f"Try '{clue}' to get you going! ",
               f"Have a go at '{clue}' and see how you get on! ",
               f"One from the archives: '{clue}'. "]
    ends = [f"Check it out here: {url}",
            f"The whole crossword can be found here: {url}",
            f"Have a go at the whole puzzle here: {url}"]
    return choice(openings) + choice(middles) + choice(ends)


def main():
    with open('./clues.pickle', 'rb') as f:
        clues = pickle.load(f)
    crossword_id = get_crossword_id()
    if crossword_id in [clue.xword_id for clue in clues]:
        pass  # return  # This crossword is already in the database
    todays_clues = scrape_clues(crossword_id)
    clues += todays_clues
    with open('./clues.pickle', 'wb') as f:
        pickle.dump(clues, f)  # Save the new clues just scraped
    setter = todays_clues[0].setter

    patterns = defaultdict(list)
    setters = defaultdict(list)
    for clue in clues:
        *words, pattern = clue.raw_clue.split()
        patterns[len(words)].append(pattern)  # For tacking on eg. (3,4)
        setters[clue.setter].append(' '.join(words))  # Every clue by a setter

    if setter in setters.keys():
        if len(setters[setter]) > 500:
            model = markovify.NewlineText(setters[setter])
    else:
        model = markovify.NewlineText([clue for setter in setters.keys()
                                       for clue in setters[setter]])
    clue = model.make_short_sentence(50)
    clue += ' ' + choice(patterns[len(clue.split())])

    tweet = make_tweet(setter, crossword_id, clue)
    print(tweet)

    api = Twython(**credentials)
    api.update_status(status=tweet)


if __name__ == '__main__':
    main()
