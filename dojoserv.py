import sys; sys.path.append('lib/')


import os
join = os.path.join
exists = os.path.exists


import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.web import HTTPError
from markdown import markdown

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

        tornado.web.Application.__init__(self, handlers, **settings)
 


class MainHandler( tornado.web.RequestHandler):
    def get(self):

        txt = open( 'docs/hello.txt').read()
        doc = markdown( txt)
        self.render( 'doc.html', doc=doc)


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

    tornado.options.parse_command_line()

    if options.runtests:
        #put tests in the tests folder
        import tests, unittest
        import sys
        sys.argv = ['dojoserv.py',] #unittest goes digging in argv
        unittest.main( 'tests')
        return

    http_server = tornado.httpserver.HTTPServer( App() )
    http_server.listen(options.port)
    print 'Serving on port %d' % options.port
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

