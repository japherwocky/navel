from tornado.web import HTTPError, RequestHandler
from formencode import Invalid
import json

from model import db
import model.restrictions as orm
from storm.zope.zstorm import global_zstorm
from storm.exceptions import NoStoreError
from time import time

from logging import warning, debug


class AuthMixin:
    _user = None
    def get_current_user(self):
        if self._user: return self._user
        session = self.db.find( self.get_cookie("session"))

        #skip session cookie, hash ip+user-agent?
        #check for session cookie, or set to hash( ip+user-agent)

        #check in datastore for session
        if not session or not find(session): 
            raise HTTPError( 403)

        return 'username'


    @property
    def user(self): return self.get_current_user()


import smtplib
import httplib
import email
#m = email.message.Message()
class MailAlertMixin( object):
    def send_error( self, status, **kwargs):
        """
        Unfortunately, it seems like tornado is currently reworking their error
        handling, to pass an "exc_info" triplet instead of "exception".  Probably
        this will break on a tornado upgrade
        """

        if self._headers_written:
            logging.error("Cannot send error response after headers written")
            if not self._finished:
                self.finish()
            return
        self.clear()
        self.set_status(status)
        message = self.get_error_html(status, **kwargs)
        self.finish(message)

        if str(status).startswith('4'): return

        try:
            info( 'Errors!  Attempting to email someone(s).')        

            S = smtplib.SMTP( 'localhost')

            m = email.message_from_string('')
            m['From'] = 'rheo@loud3r.com'
            m['Reply-to'] = 'team@loud3r.com'
            m['Subject'] = 'RheoFail: %d %s'% (status,httplib.responses[status])

            msg = ''

            if 'exception' in kwargs:
                import traceback
                msg += traceback.format_exc()

            from tornado.options import options
            if options.log_file_prefix:
                msg += "\nLast 50 Lines of logfile:\n\n"
                msg += ''.join( open(options.log_file_prefix).readlines()[-50:])
            

            m.set_payload( msg)

            recipients = ['japhy@loud3r.com',]

            for recip in recipients:
                while 'To' in m:
                    del m['To']

                m['To'] = recip
                S.sendmail( m['Reply-to'], recip, m.as_string())

        except Exception, e:
            warning( Exception)
            warning( e)
            warning( "Failed to mail errors")

