import os
import time
import urllib2

INTERVAL = None

CATEGORIES = [
    'arts',
    'cbbc',
    'cbeebies',
    'comedy',
    'documentaries',
    'drama-and-soaps',
    'entertainment',
    'films',
    'food',
    'history',
    'music',
    'news',
    'science-and-nature',
    'sport',
    'audio-described',
    'signed',
    'northern-ireland',
    'scotland',
    'wales',
]

CHANNELS = [
    'bbcone',
    'bbctwo',
    'bbcthree',
    'bbcfour',
    'cbbc',
    'cbeebies',
    'bbcnews',
    'bbcparliament',
    'bbcalba',
]

BASEURL = "http://bbc.co.uk/"

if __name__ == '__main__':
    urls = []

    for channel in CHANNELS:
        urls.append(channel)

    for category in CATEGORIES:
        urls.append("iplayer/categories/" + category)
        urls.append("iplayer/categories/" + category + "/all?sort=dateavailable")

    urls.append("iplayer/group/most-popular")
    urls.append("iplayer")

    while True:
        dirname = str(int(time.time()))
        os.mkdir(dirname)

        print dirname
        print "---"

        for url in urls:
            print url
            filename = url.replace("/", "-") + ".html"
            filestream = open(dirname + "/" + filename, 'w')
            filestream.write(urllib2.urlopen(BASEURL + url).read())
            filestream.close()

        if INTERVAL is not None:
            print
            time.sleep(INTERVAL)
        else:
            break

