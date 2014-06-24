import os
import time
import urllib2


class IplayerGrab:

    categories = [
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

    channels = [
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

    baseurl = 'http://bbc.co.uk/'

    def __init__(self, dirname):
        self._urls = self._generate_urls()
        self._dirname = str(dirname)

        os.mkdir(self._dirname)

    def _generate_urls(self):
        urls = []

        for channel in self.channels:
            urls.append(channel)

        for category in self.categories:
            urls.append('iplayer/categories/' + category)
            urls.append('iplayer/categories/' + category + '/all?sort=dateavailable&page={PAGE}')
            urls.append('iplayer/categories/' + category + '/all?sort=atoz&page={PAGE}')

        urls.append('iplayer/group/most-popular')
        urls.append('iplayer')

        return urls

    def _save_page(self, url):
        page = urllib2.urlopen(self.baseurl + url).read()

        if '<p class="error-message">' in page:
            return False

        filename = url.replace('/', '-') + '.html'
        filestream = open(self._dirname + '/' + filename, 'w')
        filestream.write(page)
        filestream.close()

        return True

    def run(self, printprogress=False):
        for url in self._urls:
            if printprogress:
                print url

            if '{PAGE}' in url:
                pagecounter = 1
                while True:
                    pageurl = url.replace('{PAGE}', str(pagecounter))

                    if not self._save_page(pageurl):
                        break

                    pagecounter += 1
                    print pageurl

            else:
                self._save_page(url)

if __name__ == '__main__':
    IplayerGrab(dirname=int(time.time())).run(printprogress=True)
