import webapp2
import sys

from Handlers.BaseHandler import *
from Handlers.ImageHandler import *
from Models.UserModels import *
from Handlers.AccountHandler import *
from Handlers.ProfileHandler import *
from Handlers.RouteHandler import *
from Handlers.Launch.CLHandler import *
from Handlers.ReservationHandler import *
from Handlers.SearchHandler import *
from Handlers.ExpireHandler import *
from Handlers.SummaryHandler import SummaryHandler
from Handlers.SettingsHandler import *
from Handlers.DriverHandler import *
from Handlers.Tracker.TrackerHandler import *
from Handlers.Launch.MobileHandler import *
from Utils.DebugUtils import *
from Utils.EmailUtils import *
from Utils.CloseUtils import *
from Utils.ErrorUtils import *

## Launch!
from Handlers.Launch.ApplyHandler import *
from Handlers.Launch.RequestHandler import *
from Handlers.Launch.ReserveHandler import *
from Handlers.Launch.CheckoutHandler import *

from Pages.HomePage import *
from Pages.ContactPage import *

from Handlers.MessageHandler import *
from Handlers.ReviewHandler import *

sys.path.append('/Pages')

app = webapp2.WSGIApplication([('/', HomePage),
                                ('/home', GuestPage),
                                ('/splash', SplashPage),
                               ('/img/([0-9]+)', ImagePage),
# LAUNCH!
# requests
    webapp2.Route('/res/<action>/<key>', handler=ReserveHandler),
    webapp2.Route('/res/<action>', handler=ReserveHandler),
    webapp2.Route('/res', handler=ReserveHandler),
    webapp2.Route('/request', handler=RequestHandler),
   webapp2.Route('/apply', handler=ApplyHandler),
   webapp2.Route('/apply/<action>', handler=ApplyHandler),
   webapp2.Route('/checkout', handler=CheckoutHandler),
   webapp2.Route('/checkout/<key>', handler=CheckoutHandler),
# scrape
   webapp2.Route('/scraped/<key:[\w\-]{20,}>', handler=CLHandler),
   webapp2.Route('/scraped/<action>/<key:[\w\-]{20,}>', handler=CLHandler),
# mobile driver tracker
   webapp2.Route('/mobile/<action>', handler=MobileHandler),
   webapp2.Route('/track/<action>', handler=TrackerHandler),
   webapp2.Route('/track/<action>/<key:[\w\-]{20,}>', handler=TrackerHandler),
# search
   webapp2.Route('/search', handler=SearchHandler),
   webapp2.Route('/search/<action>', handler=SearchHandler),
   webapp2.Route('/search/<action>/<key:[\w\-]{20,}>', handler=SearchHandler),
# accounts
   webapp2.Route('/signup', handler=SignupPage),
   webapp2.Route('/signup/<action>', handler=SignupPage),
   ('/signout', SignoutPage),
   ('/account', AccountPage),
   webapp2.Route('/settings', handler=SettingsHandler),
   webapp2.Route('/settings/<action>', handler=SettingsHandler),
# profile
    webapp2.Route('/drive', handler=DriverHandler),
    webapp2.Route('/profile/<key:[\w\-]{20,}>', handler=ProfileHandler),
    webapp2.Route('/profile/<action>', handler=ProfileHandler),
    webapp2.Route('/profile', handler=ProfileHandler),
    webapp2.Route('/routes', handler=DumpHandler),
# post routes
    webapp2.Route('/post/<action>/<key:[\w\-]{20,}>', handler=RouteHandler),
    webapp2.Route('/post/<key:[\w\-]{20,}>', handler=RouteHandler),
    webapp2.Route('/post/<action>', handler=RouteHandler),
    webapp2.Route('/post', handler=RouteHandler),
# reservations
    webapp2.Route('/reserve/<action>/<key:[\w\-]{20,}>', handler=ReservationHandler),
    webapp2.Route('/reserve/<key:[\w\-]{20,}>', handler=ReservationHandler),
# message
    webapp2.Route('/message', handler=MessageHandler),
    webapp2.Route('/message/<action>', handler=MessageHandler),
    webapp2.Route('/message/<action>/<key:[\w\-]{20,}>', handler=MessageHandler),
# reviews
   webapp2.Route('/review', handler=ReviewHandler),
   webapp2.Route('/review/<action>', handler=ReviewHandler),
# Utils
   ('/navhead',NavHelper),
   ('/suicide',CloseHelper),
# Footer
   ('/loc', LocationPage),
   ('/about', AboutPage),
   ('/how', HowItWorksPage),
   ('/privacy', PrivacyPage),
   ('/tos', TOSPage),
   ('/jobs', JobsPage),
    webapp2.Route('/blog', handler=BlogPage),
    webapp2.Route('/blog/<post>', handler=BlogPage),
   ('/contact', ContactPage),
# Admin
    webapp2.Route('/debug/<action>', handler=DebugUtils),
   ('/summary', SummaryHandler),
   ('/expire', ExpireHandler), EmailHandler.mapping()],
  debug=True)

app.error_handlers[400] = ErrorHandler400
app.error_handlers[403] = ErrorHandler403
app.error_handlers[404] = ErrorHandler404
app.error_handlers[409] = ErrorHandler409
app.error_handlers[408] = ErrorHandler408
app.error_handlers[500] = ErrorHandler500
