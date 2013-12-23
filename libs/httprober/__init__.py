import webapp2
import sys

class prober():
    """HTTP Information Prober"""
    CrLf = "<br>"

    def __init__(self, request, response):
        self.request = request        
        self.response = response
        self.response.write("<title>Echo Message</title>")

    def writeInfo(self):
        self.writeRequestInfo()
        self.writeHeaders()
        self.writeCookies()
        self.writeRequestBody()
        self.writeParams()

    def writeRequestInfo(self):
        self.println("System Info:")
        self.println("Python version:" + sys.version)
        self.println("----Start Request Info----")
        self.println("Request from: " + self.request.remote_addr)
        self.println("Full URL requested: " + self.request.url)
        self.println("Request Path: " + self.request.path)
        self.println("Query string: " + self.request.query_string) 
        self.println("----End Request Request----")
        self.println()

    def writeHeaders(self):
        self.println("----Start Header List----")
        for key in self.request.headers:
            self.println("Key: " + key + " Value: " + self.request.headers[key])
        self.println("----End Header List----")
        self.println()

    def writeCookies(self):
        self.println("----Start Cookies----")
        for key in self.request.cookies:
            self.println("Key: " + key + " Value: " + self.request.cookies[key])
        self.println("----End Cookies----")
        self.println()

    def writeRequestBody(self):
        self.println("----Start Request Body----")
        self.println(self.request.body)
        self.println("----End Request Body----")
        self.println()

    def writeParams(self):
        get_params = self.request.GET
        post_params = self.request.POST
        self.println("----Start Paramaters in GET----")
        for key in get_params:
            self.println("Key: " + key + " Value: " + get_params.get(key))
        self.println("----End Paramaters in GET----")
        self.println()

        self.println("----Start Paramaters in POST----")
        for key in post_params:
            
            if isinstance(post_params[key],buffer) or isinstance(post_params[key],basestring):
                self.println("Key: " + key + " Value: " + post_params.get(key))
            else:
                self.println("Key: " + key + " Value: Instance of " + post_params[key].__class__.__name__)

        self.println("----End Paramaters in POST----")

        self.println()


    def println(self,info=""):
        self.__print(info + "<br>")

    def __print(self,info):
        self.response.write(info)        