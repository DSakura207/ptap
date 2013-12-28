import webapp2
import urlparse
import logging

class TransparentProxy(webapp2.RequestHandler):
    """Transparent forward all request to Twitter"""

    def get(self):
        self.do_proxy('GET')

    def post(self):
        self.do_proxy('POST')

    def do_proxy(self, method):
        # parse requested path and query string.
        parsed_result = urlparse.urlparse(self.request.url)
        path, qs = parsed_result.path[6:], parsed_result.query

        logging.info("T Mode, requested: %s, QueryString is %s" % (path, qs))
        logging.debug("Request headers:")
        logging.debug(self.request.headers)
        logging.debug("Request body:")
        logging.debug(self.request.body)

        import httplib
        headers = []
        logging.debug("Building request.")
        for key in self.request.headers:

            # skip some headers to silence GAE.
            if key == 'Content_Length' or key == 'Host':
                continue
            headers.append((key, self.request.headers[key]))

        conn = httplib.HTTPSConnection('api.twitter.com')

        try:
            conn.request(method, path + '?' + qs, self.request.body, dict(headers))
            res = conn.getresponse()
            
            logging.info("Got response from Twitter.")
            logging.info("Write HTTP headers.")
            logging.debug("HTTP headers:")
            logging.debug(res.getheaders())
            for key, value in res.getheaders():
                # skip some headers to silence GAE.
                if key == 'Host':
                    continue
                self.response.headers.add(key, value)
            
            s = res.read()    
            self.response.write(s)
            logging.info("Response body is written.")
            logging.debug("Response body:")
            logging.debug(s)
        except Exception, e:
            logging.error(e)
            self.abort(500)


app = webapp2.WSGIApplication([
    (r'/api/t/.*', TransparentProxy),
], debug=False)