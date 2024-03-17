from bs4 import BeautifulSoup
import requests

base_url = 'https://safebooru.org/index.php?page=post'
s = requests.session()
s.headers.update({'User-Agent': 'booru2tg. I have read your ToS, but i need to receive images via tg. ' +
                                'Sorry, if you think this is spam, contact me via github issues: '
                                'https://github.com/sdfdasofdosfidsjuof/booru2tg/issues'})


def giv_me_40_divided_next():
    n = 1
    while True:
        yield 40 * n
        n += 1


divided_by40N = giv_me_40_divided_next()


# https://safebooru.org/index.php?page=post &s=list &tags=tag
def get_ids_by_tag(tag: str) -> str:
    """
    function to get string of ids by tag

    :param tag: tag on booru-sites
    :return: str of tags separated by CRLF
    """
    url = f'{base_url}&s=list&tags={tag}'
    out = ''
    while url:
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = soup.find("h1")
        if h1 is not None:
            match h1.text:
                case 'Search is overloaded! Try again later...':
                    if out == '':
                        raise Exception('Search overloaded')
                    else:
                        with open("log_down_link.txt", 'a') as file:
                            file.write(url)
                        return out
                case 'Nothing found, try google? ':
                    raise Exception('Not found')

        content = soup.find('div', class_='content')
        posts = content.find_all('span', {'class': 'thumb'})

        for post in posts:
            link = post.find('a')['href']
            post_id = link[30:]
            out += f'{post_id}\n'
        if content.find('a', {'alt': 'next'}) != '':
            url = f'{base_url}&s=list&tags={tag}&pid={next(divided_by40N)}'
    return out


def get_image_link_by_id(image_id: str) -> str:
    link = f'{base_url}&s=view&id={image_id}'
    response = s.get(link)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.find("img", {'id': 'image'}).get('src')
