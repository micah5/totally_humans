__author__  = "Micah Price"
__email__   = "98mprice@gmail.com"

import config
import praw

reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     user_agent=config.user_agent)

def write_to_file(list, name):
    with open('data/%s.txt' % name, 'w') as f:
        for item in list:
            f.write("%s\n<break>\n" % item)

def parse_reddit(n):
    print(reddit.read_only)

    titles = []
    comments = []
    for submission in reddit.subreddit('totallynotrobots').new(limit=n):
        titles.append(submission.title)
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            comments.append(comment.body)
    return titles, comments

titles, comments = parse_reddit(1000)
write_to_file(titles, 'titles')
write_to_file(comments, 'comments')
