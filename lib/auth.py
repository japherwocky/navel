class Logout( AuthHandler):
    def get(self):
        self.clear_cookie("pearachuteuser")
        self.redirect("/")

class Login( AuthHandler):
    def get( self, errormsg=None):
        next = self.get_argument("next", None)
        self.render( 'login.html', next=next, errormsg=errormsg)

    def post( self):
        login = self.get_argument( 'login', None)
        password = self.get_argument( 'password', None)

        if not password or not login:
            return self.get( "please enter both a name and a password")

        userobj = M[db].users.find_one( {'user':login.lower()})
        if not userobj: return self.get( "Invalid login or password!")

        if not sha512( password).hexdigest() == userobj['passhash']:
            return self.get( "Invalid login or password!" )

        self.set_secure_cookie("banneruser", login)

        nexturl = self.get_argument('next', None)
        self.redirect( nexturl or '/')

