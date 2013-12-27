PTAP
====

A Twitter api proxy in Python based on GAE.

This is a Twitter API proxy. You do not know what it is? Fine, then you do not need it.

To those who need to use this:


Step 1:

You MUST change the customer key/secret pair in api.py to use PTAP to use it like twip O mode.

You MUST change the "application" part in app.yaml to match your GAE application. Or you need to give an arguement to appcfg.py.

Register a GAE application and a Twitter application. 

When Twitter asks you callback URL, you should fill in something like this:

https://example.appspot.com/api/callback

Change the customer key/secret pair in api.py. 

Deploy your PTAP using Google App Engine Launcher, or in CLI.


Step 2:

You could use PTAP like twip. 

When you fill in REST API url:

You might to add 1.1/ at the end of url.

You have two choices for REST API url:

https://example.appspot.com/api/t/ 

Request is simply forwarded to Twitter. This is just like twip's T mode.

https://example.appspot.com/api/o/your-UID/

Request will be resigned and sent to Twitter. This is just like twip's O mode.

You need to access https://example.appspot.com/ to authorize PTAP first.
