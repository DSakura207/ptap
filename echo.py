#!/usr/bin/env python
#
#
#
#
"""Echo the http request send to this uri."""


# Add library path
import library

# Put all third-party libraries under /lib, and put import clauses below this line.
import httprober


import webapp2

class MainHandler(webapp2.RequestHandler):
    def get(self):
        p = httprober.prober(self.request, self.response)
        p.writeInfo()

    def get(self):
        p = httprober.prober(self.request, self.response)
        p.writeInfo()

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
