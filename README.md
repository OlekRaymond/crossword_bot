# crossword_bot

This is a twitter bot for making up guardian cryptic crossword clues
depending on the setter on the day. However, the clues have have no answers,
they just look and sound like clues.

The bot itself relies on two packages, markovify to make a new clue based on
old clues, and twython to interact with twitters API. All of the clues from
the last twenty years are stored in clues.pickle.

When the bot runs the following happens:
1. The most recent cryptic crossword number is found. If it is a new one (ie. it
  is not the weekend) we move on to step 2, otherwise return None.
2. The most recent author and all of the clues found are taken from the
web page. The new clues are added to the clues.pickle database.
3. If the setter is known, and has more than 500 clues in the database then a
new clue is made using a markov chain based on their previous clues. otherwise
a clue is made from the whole database.
4. A tweet is formulated from a few possible sentences (start, middle, end),
with the setter @'ed if they are on twitter.
