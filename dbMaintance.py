import webapp2
import api
import logging

class ClassName(webapp2.RequestHandler):
    def post(self):
        pass
        
    def get(self):
        isScheduledRequest = True if self.request.get('X-Appengine-Cron') else False
        if isScheduledRequest:
            logging.info("Starting DB maintance:")
            logging.info("Remove non-access tokens:")
            dbClean()
            logging.info("Remove non-access tokens completed.")
        else:
            # This is for testing. A page should displayed if the request is not by GAE.
            logging.info("Starting DB maintance:")
            logging.info("Remove non-access tokens:")
            dbClean()
            logging.info("Remove non-access tokens completed.")

    def dbClean(self):
        nonAccessToken = api.Token.query(Token.isAccessToken == False)
        it = nonAccessToken.iter()
        nonAccessTokenCount = nonAccessToken.count()
        logging.info("Query result: %d non-access token(s) found" % (nonAccessTokenCount,))
        while nonAccessToken.has_next():
            nonAccessToken = nonAccessToken.next()
            nonAccessToken.key.delete()
            nonAccessTokenCount--
        logging.info("Maintance result: %d non-access token(s) deleted" % (nonAccessTokenCount,))
