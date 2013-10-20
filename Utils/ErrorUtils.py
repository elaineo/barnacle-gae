import logging
import jinja2
import os

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader('templates/err'), autoescape = True)

# Bad Request
def ErrorHandler400(request, response, exception):
    logging.exception(exception)
    t = jinja_env.get_template("err400.html")
    response.write(t.render())
    response.set_status(400)

# Forbidden    
def ErrorHandler403(request, response, exception):
    logging.exception(exception)
    t = jinja_env.get_template("err403.html")
    response.write(t.render())
    response.set_status(403)
    
# Not Found    
def ErrorHandler404(request, response, exception):
    logging.exception(exception)
    t = jinja_env.get_template("err404.html")
    response.write(t.render())
    response.set_status(404)

# Whatever I want 
def ErrorHandler409(request, response, exception):
    logging.exception(exception)
    t = jinja_env.get_template("err494.html")
    response.write(t.render())
    response.set_status(404)
    
# Request Timeout    
def ErrorHandler408(request, response, exception):
    logging.exception(exception)
    t = jinja_env.get_template("err408.html")
    response.write(t.render())
    response.set_status(408)    
    
# Internal Server Error    
def ErrorHandler500(request, response, exception):
    logging.exception(exception)
    t = jinja_env.get_template("err500.html")
    response.write(t.render())
    response.set_status(500)    