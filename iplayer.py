import re
import urllib2

from altplayer import db

CATEGORIES = {
    'arts': "Arts",
    'cbbc': "CBBC",
    'cbeebies': "CBeebies",
    'comedy': "Comedy",
    'documentaries': "Documentaries",
    'drama-and-soaps': "Drama & Soaps",
    'entertainment': "Entertainment",
    'films': "Films",
    'food': "Food",
    'history': "History",
    'music': "Music",
    'news': "News",
    'science-and-nature': "Science & Nature",
    'sport': "Sport",
    'audio-described': "Audio Described",
    'signed': "Signed",
    'northern-ireland': "Northern Ireland",
    'scotland': "Scotland",
    'wales': "Wales",
}

class _Sync:

    _re_page_num = re.compile('>(\d+)<')
    _re_pid = re.compile('/iplayer/episode/([a-z0-9]+)/')
    _re_title = re.compile('<div class="title top-title">(.+)</div>')
    _re_subtitle = re.compile('<div class="subtitle"> (.*) </div>   <p')
    _re_episodes = re.compile('/iplayer/episodes/([a-z0-9]+)">')
    _re_synopsis = re.compile('<p class="synopsis"> (.*) </p> <p>')
    _re_availability = re.compile('<span class="availability"> (.*) left')
    _re_duration = re.compile('(\d+) mins?')
    _re_brand = re.compile('<span class="medium">([^<]+)')
    _re_imgid = re.compile('http://ichef\.bbci\.co\.uk/images/ic/336x189/(legacy/episode/[a-z0-9]+|[a-z0-9]+)\.jpg')

    def __init__(self, programmes_collection, print_progress=False):
        self._programmes_collection = programmes_collection
        self._print_progress = print_progress

    def _parse_page_nums_html(self, html):
        return self._re_page_num.findall(html)

    def _parse_programme_html(self, html):
        lines = html.split('\n')
        programme = {}

        programme['pid'] = self._re_pid.search(lines[0]).group(1)

        programme['title'] = self._re_title.search(lines[0]).group(1)

        episodes_search = self._re_episodes.search(lines[1])
        if episodes_search is not None:
            programme['episodes'] = episodes_search.group(1)

        subtitle_search = self._re_subtitle.search(lines[1])
        if subtitle_search is not None:
            programme['subtitle'] = subtitle_search.group(1)

        programme['synopsis'] = self._re_synopsis.search(lines[1]).group(1)

        availability_search = self._re_availability.search(lines[1])
        if availability_search is not None:
            programme['availability'] = availability_search.group(1)

        programme['duration'] = self._re_duration.search(lines[1]).group(1)

        brand_search = self._re_brand.search(lines[1])
        if brand_search is not None:
            programme['brand'] = brand_search.group(1)

        programme['imgid'] = self._re_imgid.search(lines[0]).group(1)

        return programme

    def _print(self, output):
        if self._print_progress:
            print(output)

    def _programme_string(self, programme):
        string = ''
        
        if 'category' in programme:
            string += programme['category'] + '/'
        else:
            string += '\t/'

        if 'episodes' in programme:
            string += programme['episodes'] + '/'

        string += programme['pid'] + '/'
        string += programme['title'] + '/'

        if 'subtitle' in programme:
            string += programme['subtitle'] + '/'

        return string

    def _pull_category_page(self, category_id, page_num, episodes=False):
        if not episodes:
            url = ("http://www.bbc.co.uk/iplayer/categories/" + category_id
                + "/all?sort=dateavailable&page=" + str(page_num))
        else:
            url = ("http://www.bbc.co.uk/iplayer/episodes/" + category_id
                + "?page=" + str(page_num))

        data = urllib2.urlopen(url).read()

        page = {}
        page['programmes'] = []

        programme_counter = 0
        prev_programme_line = ''
        for line in data.split('\n'):
            if ('<div class="play-icon">' in line
                or '<div id="blq-content"' in line):
                if prev_programme_line == '':
                    prev_programme_line = line
                    continue

                programme_counter += 1

                if episodes and programme_counter < 2:
                    continue

                programme = self._parse_programme_html(prev_programme_line
                    + '\n' + line)
                
                if not episodes:
                    programme['recency_rank'] = (page_num * 100
                        + programme_counter)

                if not episodes:
                    programme['category'] = category_id
                else:
                    programme['episodes'] = category_id

                page['programmes'].append(programme)
                prev_programme_line = line

                self._print(self._programme_string(programme))

            if '<li class="page focus">' in line:
                page_nums = self._parse_page_nums_html(line)
                page['max_page_num'] = int(page_nums[-1])

        if 'max_page_num' not in page:
            page['max_page_num'] = 1

        return page

    def _sync_category(self, category_id, episodes=False):
        page_counter = 1
        programmes = []
        while True:
            page = self._pull_category_page(category_id, page_counter,
                episodes)

            for programme in page['programmes']:
                if not episodes and 'episodes' in programme:
                    programmes.append(
                        self._sync_category(programme['episodes'],
                            episodes=True)
                    )

                pid = programme['pid']

                self._programmes_collection.update({'pid': pid}, programme,
                    upsert=True)

                programmes.append(programme)

            if page['max_page_num'] == page_counter:
                break

            page_counter += 1

        return programmes

    def run(self):
        programmes_count = 0
        for category_id in CATEGORIES:
            programmes_count += len(self._sync_category(category_id))

        self._print("")
        self._print("Found " + str(programmes_count) + " programmes.")


def run_sync(print_progress=False):
    _Sync(db.programmes_tmp, print_progress=print_progress).run()
    
    db.programmes.drop()
    db.programmes_tmp.rename('programmes')

    if print_progress:
        print("Programmes collection updated.")
