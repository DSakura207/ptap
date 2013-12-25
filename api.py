import library

import oauth2 as oauth
import httprober

import urlparse
import os
import webapp2
import jinja2
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

twitter_base_url = 'https://api.twitter.com/'
consumer_key = '30gj5ywcZA8tPf7DofyZDQ'
consumer_secret = 'ZOd0Wg56h7D9EHrCkvdz5QGCS5yLFHWDOnRH6wCce7E'
request_token_url = twitter_base_url + 'oauth/request_token'
access_token_url = twitter_base_url + 'oauth/access_token'
authorize_url = twitter_base_url + 'oauth/authorize'

        
class Token(ndb.Model):
    """Data model for access token"""
    
    UID = ndb.StringProperty(required = True)
    key = ndb.StringProperty(required = True)
    secret = ndb.StringProperty(required = True, indexed = False)
                        

class CallbackHandler(webapp2.RequestHandler):
    """docstring for CallbackHandler"""
    
    def get(self):
        
        callback_token = dict(urlparse.parse_qsl(self.request.query_string))
        # Query saved request token from db.
        saved_token = Token.query(Token.key == callback_token['oauth_token']).get()

        # If we cannot get anything, the token in callback is illgeal.
        if saved_token == None:
            template_values = {
            'error_code': 'Internal Error',
            'error_reason': 'Could not found a matched request token from callback.',
            }
            template = JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(template_values))
            return

        # create token from saved request token and received verifier
        token = oauth.Token(saved_token.key,
                        saved_token.secret)
        token.set_verifier(callback_token['oauth_verifier'])
        # get access token from server.
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer, token)
        resp, content = client.request(access_token_url, "POST")
        # parse token, and look up whether a same key/secret pair is found.
        access_token = dict(urlparse.parse_qsl(content))
        exist_token = Token.query(Token.key == access_token['oauth_token']).get()

        # Add that UID with key/secret combination.
        # When we found the same key/secret combination with a different UID,
        # We keep the previous record, but we will notice user about this.
        saved_token.key = access_token['oauth_token']
        saved_token.secret = access_token['oauth_token_secret']
        saved_token.put()


        if exist_token and exist_token.secret == access_token['oauth_token_secret']:
            title = 'Another UID added'
            message = 'You now have more names.'
            detail = 'We have added a custom URL for you, besides, we found you already have a custom URL.\n'
            detail += 'In order to keep things working normally, the previous one is not touched.\n'
            import_message = 'However, please keep them privately. Anyone can send tweet using your URL.'
            
        else:
            title = 'Custom URL created'
            message = 'You could use PTAP now.'
            detail = 'Please keep your custom URL privately.'
            import_message = 'Anyone can send tweet using your URL.'

        custom_url = 'https://' + self.request.host + '/api/' + saved_token.UID + '/'


        template_values = {
            'title': title,
            'message': message,
            'detail': detail,
            'import_message': import_message,
            'custom_url': custom_url,
            }
        template = JINJA_ENVIRONMENT.get_template('success.html')
        self.response.write(template.render(template_values))
        
class AuthorizeAPI(webapp2.RequestHandler):
    """Authroize PTAP."""

    def post(self):
        # determine if UID exist. if so, redirect back to UID setting page.
        id = self.request.get('UID')
        isUIDexist = Token.query(Token.key == id).get()
        if isUIDexist:
            self.redirect('/api/authorize_me')
            return

        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)
        resp, content = client.request(request_token_url, "GET")
        if resp['status'] != '200':
            template_values = {
            'error_code': resp['status'],
            'error_resaon': resp['reason'],
            }
            template = JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(template_values))
        else:
            request_token = dict(urlparse.parse_qsl(content))
            self.redirect("%s?oauth_token=%s" % (authorize_url, request_token['oauth_token']))
            token = Token(UID = id, key = request_token['oauth_token'], secret = request_token['oauth_token_secret'])
            token.put()
        
class APIproxy(webapp2.RequestHandler):
    """docstring for APIproxy"""
    def get(self):
        self.do_proxy('GET')

    def post(self):
        self.do_proxy('POST')

    def do_proxy(self, method):
        # parse raw path and query string.
        parsed_result = urlparse.urlparse(self.request.url)
        raw_path, qs = parsed_result.path[5:], parsed_result.query


        # get UID and requested path. If we could not get two pieces of things, we end with IndexError
        try:
            uid, path = raw_path.split('/', 1)[0], raw_path.split('/', 1)[1]
        except IndexError, e:
            self.abort(400)
        
        # try to retrieve saved token by uid. If we could not retrieve one, we can do nothing.
        token_query = Token.query(Token.UID == uid).get()
        if token_query == None:
            self.abort(400)

        # request information from server.
        token = oauth.Token(token_query.key, token_query.secret)
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer, token)
        request_url = twitter_base_url + path
        server_res, server_content = client.request(request_url, method, self.request.body, self.request.headers)

        # clear response, add retrieved information.
        self.response.clear()


        for key in server_res.keys():
            self.response.headers.add(key, str(server_res.get(key)))
            #self.response.write(key + '=' + server_res.get(key) + '<br>')

        self.response.write(server_content)









        

app = webapp2.WSGIApplication([
    ('/api/authorize_me', AuthorizeAPI),
    (r'/api/callback\?*', CallbackHandler),
    (r'/api/.*', APIproxy),
], debug=True)