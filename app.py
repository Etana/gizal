import functools
import requests
from werkzeug.wrappers import Request, Response
from urllib.parse import unquote
from cgi import escape

# main application

@Request.application
def application(request):
    # request.path = '/'
    if request.query_string:
        action, _, query = request.query_string.decode().partition('=')
        query = unquote(query)
        domain, _, path_qs = query.partition('://')[2].partition('/')
        content = domain_map.get(domain, lambda *a: None)(query, domain, path_qs)
    else:
        content = '<form><input name=q></form>'
    return Response(content, mimetype='text/html')

# tools

def between(start, end, content):
    """ Return text between start and end string or None """
    return before(end, after(start, content))

def after(start, content):
    try:
        return content[content.index(start) + len(start):]
    except:
        return ''

def before(end, content):
    try:
        return content[:content.index(end)]
    except:
        return ''

# domain handlers

domain_map = {}
def domain(domain):
    def domain_decorator(func):
        domain_map[domain] = func
        return func
    return domain_decorator

@functools.lru_cache(maxsize=None)
@domain('wiki.d-addicts.com')
def wiki_daddicts(query, domain, path_qs):
    print(path_qs)
    content = ''
    page = requests.get(query).text
    if '?' in path_qs or path_qs.startswith('Talk:'):
        return 'not an article =('
    title = between('"wgTitle":"', '",', page)
    tags = between('"wgCategories":["', '"],"', page).split('","')
    tags += between('<li><b>Genre:</b> ', '</li>', page).split(', ')
    tags.append(between('<li><b>Episodes:</b> ', '</li>', page))
    actor_block = between('<h2><span class="mw-headline" id="Cast">Cast</span></h2>', '<h2>', page)
    for actor_line in actor_block.replace('\n', '').split('</li><li>'):
        role_part = after('</a> as ', actor_line)
        if role_part:
            tags.append(before('<', role_part) or role_part)
        actor_name = between('">', '</a>', actor_line)
        actor_link = between(' href="', '"', actor_line)
        if actor_link:
            content += wiki_daddicts('http://{}{}'.format(domain, actor_link), domain, actor_link[1:])
        tags.append(actor_name)
    content = '<h1>{}</h1><ul><li>{}</li></ul><textarea>{}</textarea>'.format(title, '</li><li>'.join(tags), escape(page))
    return content

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application, use_debugger=True, use_reloader=True)

