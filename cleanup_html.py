import os

from bs4 import BeautifulSoup
import requests

root_url = 'http://aurellem.org/society-of-mind'
root = BeautifulSoup(open('scrape20160127220531.html'))
book_title = 'Society of Mind'

# remove chapnavs & footers
[div.extract() for div in root.select('.chapnav')]
[div.extract() for div in root.select('.footer')]
[vid.extract() for vid in root.find_all('video')]


def set_title_id(title):
    # print(repr(title))
    id_prefix = title.text.split(' ')[0]

    try:
        float(id_prefix)
        _id = 'som-%s' % id_prefix
    except ValueError:
        _id = 'som-%s' % title.text

    title.attrs['id'] = _id


# set #id for link correction
for title in root.find_all('h1') + root.find_all('h2'):
    if title == book_title:
        continue

    if title.find('a'):
        continue

    set_title_id(title)

# correct links
for a in root.find_all('a'):
    link = a.attrs['href']
    if link.startswith('som-') and link.endswith('.html'):
        a.attrs['href'] = '#%s' % link[:-5]
    if link.startswith('./som-') and link.endswith('.html'):
        a.attrs['href'] = '#%s' % link[2:-5]


# also get images
for img in root.find_all('img'):
    src = img.attrs['src']
    if src.startswith('.'):
        src = src[1:]
    if src.startswith('/'):
        src = src[1:]

    parts = src.split('/')
    print(parts)
    fname = parts[-1]
    dirs = '/'.join(parts[:-1])
    path = '%s/%s' % (dirs, fname)
    try:
        os.makedirs(dirs)
    except OSError:
        print('Could not create dir')

    if os.path.exists(path):
        print('[-] file already exists')
        continue

    url = '%s/%s' % (root_url, src)
    print("Image url is: %s" % url)
    res = requests.get(url, stream=True)

    if not res.ok:
        print('[X] Error downloading file %s' % src)
        continue

    with open(path, 'wb') as target:
        target.write(res.content)

with open('scrape20160127220531-mod.html', 'w') as f:
    f.write(root.prettify().encode('utf-8'))
