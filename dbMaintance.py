import webapp2
from api import Token
import logging

class CleanDB(webapp2.RequestHandler):
    def post(self):
        pass
        
    def get(self):
        isScheduledRequest = True if self.request.get('X-Appengine-Cron') else False
        if isScheduledRequest:
            logging.info("Starting DB maintance:")
            logging.info("Remove non-access tokens:")
            self.dbClean()
            logging.info("Remove non-access tokens completed.")
        else:
            # This is for testing. A page should displayed if the request is not by GAE.
            logging.info("Starting DB maintance:")
            logging.info("Remove non-access tokens:")
            self.dbClean()
            logging.info("Remove non-access tokens completed.")

    def dbClean(self):
        nonAccessToken = Token.query(Token.isAccessToken == False)
        it = nonAccessToken.iter()
        nonAccessTokenCount = nonAccessToken.count()
        logging.info("Query result: %d non-access token(s) found" % (nonAccessTokenCount,))
        while it.has_next():
            nonAccessToken = it.next()
            nonAccessToken.key.delete()
            nonAccessTokenCount -= 1
        logging.info("Maintance result: %d non-access token(s) deleted" % (nonAccessTokenCount,))

app = webapp2.WSGIApplication([
    ('/tasks/dbMaintance', CleanDB),
], debug=True)