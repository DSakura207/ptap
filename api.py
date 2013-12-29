import library

import oauth2 as oauth
import httprober

import urlparse
import os
import logging
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
    oauth_key = ndb.StringProperty(required = True)
    oauth_secret = ndb.StringProperty(required = True, indexed = False)
                        

class CallbackHandler(webapp2.RequestHandler):
    """docstring for CallbackHandler"""
    
    def get(self):
        
        callback_token = dict(urlparse.parse_qsl(self.request.query_string))

        # If we are denied...
        if 'denied' in callback_token:
            try:
                record = Token.query(Token.oauth_key == callback_token['denied']).get()
                logging.debug(record)
                record.key.delete()
            except Exception, e:
                logging.debug(e)
            finally:
                logging.warn("Request token %s is denied. Aborted." % callback_token['denied'])

                template_values = {
                'error_code': 'Authorization Denied',
                'error_reason': 'You denied PTAP. Why?',
                }
                template = JINJA_ENVIRONMENT.get_template('error.html')
                self.response.write(template.render(template_values))
                return

        # Query saved request token from db.
        saved_token = Token.query(Token.oauth_key == callback_token['oauth_token']).get()

        # If we cannot get anything, the token in callback is illgeal.
        if saved_token == None:

            logging.error("Request token %s not found. Aborted." % callback_token['oauth_token'])

            template_values = {
            'error_code': 'Internal Error',
            'error_reason': 'Could not found a matched request token from callback.',
            }
            template = JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(template_values))
            return




        # create token from saved request token and received verifier
        logging.info("Request token found.")
        logging.debug("Saved UID: %s" % saved_token.UID)
        logging.debug("Saved request token pair: %s/%s" % (saved_token.oauth_key, saved_token.oauth_secret))

        logging.info("Token verifier retrieved.")
        logging.debug("Token verifier: %s" % callback_token['oauth_verifier'])

        token = oauth.Token(saved_token.oauth_key,
                        saved_token.oauth_secret)        
        token.set_verifier(callback_token['oauth_verifier'])
        # get access token from server.
        logging.info("Retrive access token/secret pair.")
        logging.debug("Access token/secret pair by request token verifier %s." % callback_token['oauth_verifier']) 

        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer, token)
        resp, content = client.request(access_token_url, "POST")
        # parse token, and look up whether a same key/secret pair is found.
        access_token = dict(urlparse.parse_qsl(content))
        exist_token = Token.query(Token.oauth_key == access_token['oauth_token']).get()

        logging.info("Retrived access token/secret pair.")
        logging.debug("Access token/secret pair: %s/%s" % (access_token['oauth_token'], access_token['oauth_token_secret']))
        

        # Add that UID with key/secret combination.
        # When we found the same key/secret combination with a different UID,
        # We keep the previous record, but we will notice user about this.
        saved_token.oauth_key = access_token['oauth_token']
        saved_token.oauth_secret = access_token['oauth_token_secret']
        saved_token.put()

        logging.info("Save access token/secret pair to db.")
        logging.debug("Access token/secret pair: %s/%s" % (access_token['oauth_token'], access_token['oauth_token_secret']))

        if exist_token and exist_token.oauth_secret == access_token['oauth_token_secret']:

            logging.info("Same access token/secret pair found.")

            title = 'Another UID added'
            message = 'You now have more names.'
            detail = 'We have added a custom URL for you, besides, we found you already have a custom URL.\n'
            detail += 'In order to keep things working normally, the previous one is not touched.\n'
            import_message = 'However, please keep them privately. Anyone can send tweet using your URL.'
            
        else:

            logging.info("No same access token/secret pair found.")

            title = 'Custom URL created'
            message = 'You could use PTAP now.'
            detail = 'Please keep your custom URL privately.'
            import_message = 'Anyone can send tweet using your URL.'

        custom_url = 'https://' + self.request.host + '/api/o/' + saved_token.UID + '/'

        logging.debug("Parse result html file.")

        template_values = {
            'title': title,
            'message': message,
            'detail': detail,
            'import_message': import_message,
            'custom_url': custom_url,
            }
        template = JINJA_ENVIRONMENT.get_template('success.html')
        self.response.write(template.render(template_values))

        logging.debug("Parsing completed.")
        
class AuthorizeAPI(webapp2.RequestHandler):
    """Authroize PTAP."""

    def post(self):

        logging.debug("Check UID.")
        # determine if UID exist. if so, redirect back to UID setting page.
        id = self.request.get('UID')
        isUIDexist = Token.query(Token.UID == id).get()
        if isUIDexist:

            logging.info("%s is found in db. Redirecting back." % id)

            self.redirect('/api/_authorize')
            return

        logging.debug("Request request token.")

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

            logging.error("Error occurs while requesting request token, code: %s" % resp['status'])
        else:
            request_token = dict(urlparse.parse_qsl(content))
            self.redirect("%s?oauth_token=%s" % (authorize_url, request_token['oauth_token']))

            logging.info("Retrieved request token/secret pair:" + request_token['oauth_token'] + "/" + request_token['oauth_token_secret'])

            token = Token(UID = id, oauth_key = request_token['oauth_token'], oauth_secret = request_token['oauth_token_secret'])
            token.put()

            logging.info("Saved request token/secret pair in db.")
            logging.debug("Request token/secret pair: %s/%s" % (request_token['oauth_token'], request_token['oauth_token_secret']))
        
class APIproxy(webapp2.RequestHandler):
    """docstring for APIproxy"""
    def get(self):
        self.do_proxy('GET')

    def post(self):
        self.do_proxy('POST')

    def do_proxy(self, method):
        # parse raw path and query string.
        raw_path, qs = self.request.path[7:], self.request.query_string


        # get UID and requested path. If we could not get two pieces of things, we end with IndexError
        try:
            uid, path = raw_path.split('/', 1)[0], raw_path.split('/', 1)[1]
        except IndexError, e:
            logging.error("%s is illgeal raw path. Aborted" % raw_path)
            self.abort(400)
        
        # try to retrieve saved token by uid. If we could not retrieve one, we can do nothing.
        token_query = Token.query(Token.UID == uid).get()
        if token_query == None:
            logging.error("%s is illgeal UID. Aborted" % uid)
            self.abort(400)

        # request information from server.
         
        logging.info("Request info from server.")

        token = oauth.Token(token_query.oauth_key, token_query.oauth_secret)
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer, token)
        request_url = "%s%s?%s" % (twitter_base_url, path, qs)

        logging.debug("Request address: %s, Method: %s" % (request_url, method))
        logging.debug("Request headers:")
        logging.debug(self.request.headers)

        server_res, server_content = client.request(request_url, method, self.request.body, self.request.headers)

        # clear response, add retrieved information.
        self.response.clear()

        logging.info("Add received headers.")
        logging.debug("Received headers:")
        logging.debug(server_res)
        for key in server_res.keys():
            self.response.headers.add(key, str(server_res.get(key)))
            #self.response.write(key + '=' + server_res.get(key) + '<br>')

        logging.info("Add received body.")
        logging.debug("Received body is:\n" + server_content)
        self.response.write(server_content)












        

app = webapp2.WSGIApplication([
    ('/api/authorize_me', AuthorizeAPI),
    (r'/api/callback\?*', CallbackHandler),
    (r'/api/o/.*', APIproxy),
], debug=False)