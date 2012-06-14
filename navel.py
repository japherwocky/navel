# coding=utf-8
import sys; sys.path.append('lib/')

import json
from logging import info, debug
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.web import HTTPError
from markdown import markdown

from stemming.porter2 import stem

import fuzzy
fuzz = fuzzy.DMetaphone()

import re
PUNCTUATION_CHARS = ".,;:!?@£$%^&*()-–<>[]{}\\|/'\"_#"
nopunk = re.compile( r"[%s]" % re.escape(PUNCTUATION_CHARS))
STOP_WORDS = set(["the", "of", "to", "and", "a", "in", "is", "it", "you", "that"])
MIN_WORD_LENGTH = 2
    
def text2words(text):
    if not text: return []
    text = nopunk.sub(" ", text) #strip punctuation
    words = [word.lower() for word in text.split() if len(word) >= MIN_WORD_LENGTH and word.lower() not in STOP_WORDS]
    return words


def index(filename):

    #connect to redis
    from redis import Redis
    Rtweets = Redis(db=0)
    Rstems = Redis(db=1)
    Rfuzz = Redis(db=2)

    #wipe existing indexes
    [Rtweets.delete(key) for key in Rtweets.keys()]
    [Rstems.delete(key) for key in Rstems.keys()]
    [Rfuzz.delete(key) for key in Rfuzz.keys()]
    

    def line2dict(line):
        out = {}
        out['id'], line = line.split(' ',1)
        out['username'], line = line.split('>')
        out['timestamp'], out['username'] = out['username'].split('<')
        out['toot'] = line.strip(' \n')
        return out


    #parse the tweets
    with open(filename) as f:
        tweets = f.readlines()
        for tootline in tweets:
            tweet = line2dict(tootline)
            debug( tweet['toot'])
            Rtweets.hmset( tweet['id'], tweet)
            for wordstem in [stem(w) for w in text2words( tweet['toot'])]:
                tweetdata = json.dumps( tweet)
                Rstems.zincrby( wordstem, tweetdata, int(tweet['id']))

            for fuzz0,fuzz1 in [fuzz(w) for w in text2words( tweet['toot'])]:
                if fuzz0:
                    Rfuzz.zincrby( fuzz0, tweet['id'], int(tweet['id']))
                if fuzz1:
                    Rfuzz.zincrby( fuzz1, tweet['id'], int(tweet['id']))



class App( tornado.web.Application):
    def __init__(self):
        """
        Settings for our application
        """
        settings = dict(
            cookie_secret="changemeplz",
            login_url="/login", 
            template_path= "templates",
            static_path= "static",
            xsrf_cookies= False,
            debug = True, #autoreloads on changes, among other things
        )

        """
        map URLs to Handlers, with regex patterns
        """
    
        handlers = [
            (r"/", MainHandler),
            (r"(?!\/static.*)(.*)/?", DocHandler),
            #(r"(.*)/?", DocHandler),
        ]

        from redis import Redis
        self.Rtweets = Redis(db=0)
        self.Rstems = Redis(db=1)
        self.Rfuzz = Redis(db=2)

        tornado.web.Application.__init__(self, handlers, **settings)
 


class MainHandler( tornado.web.RequestHandler):
    def get(self):

        self.render( 'search.html')

    def post(self):
        stemq = self.get_argument('stemq', False)
        if stemq:
            debug('Querying for %s by stem %s'%(stemq,stem(stemq)))
            results = self.application.Rstems.zrange( stem(stemq.lower()), 0, -1) 
            results = [json.loads(r) for r in results]

        fuzzq = self.get_argument('fuzzq', False)
        if fuzzq:
            debug('Querying for %s by fuzz %s'%(fuzzq,fuzz(fuzzq)))
            results = self.application.Rfuzz.zrange( fuzz(fuzzq)[0], 0, -1)
            results = [ self.application.Rtweets.hgetall(r) for r in results]

        self.set_header("Content-Type", "application/json") 
        self.write( json.dumps(results))
        self.finish()


class DocHandler( tornado.web.RequestHandler):
    def get(self, path):

        path = 'docs/' + path.replace('.', '').strip('/')
        if exists( path):
            #a folder
            lastname = os.path.split(path)[-1]
            txt = open( '%s/%s.txt'%( path, lastname)).read()

        elif exists( path+'.txt'):
            txt = open( path+'.txt').read()

        else:
            self.redirect('/')

        doc = markdown( txt)
        self.render( 'doc.html', doc=doc) 


def main():
    from tornado.options import define, options
    define("port", default=8001, help="run on the given port", type=int)
    define("runtests", default=False, help="run tests", type=bool)

    define("index", default=None, help="twitter_archive dump to index", type=unicode)

    tornado.options.parse_command_line()

    if options.runtests:
        #put tests in the tests folder
        import tests, unittest
        import sys
        sys.argv = ['dojoserv.py',] #unittest goes digging in argv
        unittest.main( 'tests')
        return

    if options.index:
        debug( 'Adding %s to tweet index'%options.index)
        index(options.index)

    http_server = tornado.httpserver.HTTPServer( App() )
    http_server.listen(options.port)
    info( 'Serving on port %d' % options.port )
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

