import webapp2
import sys

# Routes and Reservations
from Handlers.Post.Route import RouteHandler
from Handlers.Post.Request import RequestHandler
from Handlers.Post.Dump import DumpHandler

from Handlers.Post.Reservation import ReservationHandler
from Handlers.Post.Review import ReviewHandler

# User Accounts
from Handlers.User.Account import *
from Handlers.User.Profile import *
from Handlers.User.Dashboard import *
from Handlers.User.Settings import SettingsHandler
from Handlers.User.Driver import DriverHandler
from Handlers.User.ApplyHandler import *

#Payment Accounts
from Handlers.Money.Earnings import Earnings
from Handlers.Money.Payments import Payments
from Handlers.Launch.CheckoutHandler import *

# Cron jobs
from Handlers.Cron.ExpireHandler import *
from Handlers.Cron.Reminder import *
from Handlers.Cron.MatchHandler import *
from Handlers.Cron.SummaryHandler import SummaryHandler

from Handlers.BaseHandler import *
from Handlers.MessageHandler import *
from Handlers.ImageHandler import *
from Handlers.Launch.CLHandler import *
from Handlers.SearchHandler import *
from Handlers.NewsHandler import *
from Handlers.Admin.Gerrit import GerritHandler
from Handlers.Admin.RRDash import RRDashHandler
from Handlers.Tracker.TrackerHandler import *

from Handlers.Launch.MobileHandler import *
from Handlers.Launch.ExternalHandler import *
from Handlers.Seo.SitemapHandler import SitemapHandler, SitemapGenerationHandler
from Handlers.Seo.SearchableRouteHandler import SearchableRouteHandler
from Handlers.Seo.SearchableRequestHandler import SearchableRequestHandler
from Utils.DebugUtils import *
from Utils.EmailUtils import *
from Utils.CloseUtils import *
from Utils.ErrorUtils import *

## Launch!
from Handlers.Launch.ReserveHandler import *

from Pages.LandingPage import *
from Pages.HomePage import *
from Pages.ContactPage import *
from Pages.PromoPage import SpringBreak


sys.path.append('/Pages')

app = webapp2.WSGIApplication([('/', HomePage),
                  webapp2.Route('/img', handler=ImagePage),
                  webapp2.Route('/img/<id:[0-9]+>', handler=ImagePage),
                                ('/home', GuestPage),
                                ('/splash', SplashPage),
                                ('/springbreak', SpringBreak),
# LAUNCH!
# requests
    webapp2.Route('/res', handler=RequestHandler),  #get rid of this
    webapp2.Route('/res/<action>/<key>', handler=ReserveHandler),
   webapp2.Route('/apply', handler=ApplyHandler),
   webapp2.Route('/apply/<action>', handler=ApplyHandler),
   webapp2.Route('/checkout/<key:[\w\-]{20,}>', handler=CheckoutHandler),
   webapp2.Route('/checkout/<action>', handler=CheckoutHandler),
   webapp2.Route('/checkout/<action>/<key:[\w\-]{20,}>', handler=CheckoutHandler),
# scrape
   webapp2.Route('/scraped/<key:[\w\-]{20,}>', handler=CLHandler),
   webapp2.Route('/scraped/<action>/<key:[\w\-]{20,}>', handler=CLHandler),
# mobile driver tracker
   webapp2.Route('/mobile/<action>', handler=MobileHandler),
   webapp2.Route('/track/<action>', handler=TrackerHandler),
   webapp2.Route('/track/<action>/<key:[\w\-]{20,}>', handler=TrackerHandler),
   webapp2.Route('/tracker', handler=TrackerPage),
   webapp2.Route('/tracker/img/<resource>', handler=TrackerImageServeHandler),
   webapp2.Route('/tracker/image_upload', handler=TrackerImageUploadHandler),
   webapp2.Route('/tracker/image_upload/success/<blob_key>', handler=TrackerImageUploadSuccess),
   webapp2.Route('/tracker/image_upload_url', handler=TrackerImageUploadUrl),
# search
   webapp2.Route('/search', handler=SearchHandler),
   webapp2.Route('/search/<action>', handler=SearchHandler),
   webapp2.Route('/search/<action>/<key:[\w\-]{20,}>', handler=SearchHandler),
# seo
   webapp2.Route('/route/from/<origin>/to/<dest>', handler=SearchableRouteHandler),
   webapp2.Route('/route/from/<origin>', handler=SearchableRouteHandler),
   webapp2.Route('/route/to/<dest>', handler=SearchableRouteHandler),
   webapp2.Route('/request/from/<origin>', handler=SearchableRequestHandler),
   webapp2.Route('/request/to/<dest>', handler=SearchableRequestHandler),
   webapp2.Route('/request/from/<origin>/to/<dest>', handler=SearchableRequestHandler),
   webapp2.Route('/welcome/<action>', handler=LandingPage),
   webapp2.Route('/c/<action>', handler=CouponPage),
   webapp2.Route('/d/<action>', handler=EventPage),
   webapp2.Route('/sxsw/<action>', handler=SXSWPage),
# accounts
   webapp2.Route('/signup', handler=SignupPage),
   webapp2.Route('/signup/<action>', handler=SignupPage),
   ('/signout', SignoutPage),
   ('/account', AccountPage),
   webapp2.Route('/earn/<action>', handler=Earnings),
   webapp2.Route('/settings', handler=SettingsHandler),
   webapp2.Route('/settings/<action>', handler=SettingsHandler),
# payment account
   webapp2.Route('/pay/<action>', handler=Payments),
# profile
    webapp2.Route('/drive', handler=DriverHandler),
    webapp2.Route('/profile/<key:[\w\-]{20,}>', handler=ProfileHandler),
    webapp2.Route('/profile/<action>', handler=ProfileHandler),
    webapp2.Route('/profile', handler=ProfileHandler),
    webapp2.Route('/routes', handler=DumpHandler),
# Routes and Requests (eventually phase out posts)
    webapp2.Route('/post/<action>/<key:[\w\-]{20,}>', handler=RouteHandler),
    webapp2.Route('/post/<key:[\w\-]{20,}>', handler=RouteHandler),
    webapp2.Route('/post/<action>', handler=RouteHandler),
    webapp2.Route('/post', handler=RouteHandler),
    webapp2.Route('/route/<action>/<key:[\w\-]{20,}>', handler=RouteHandler),
    webapp2.Route('/route/<key:[\w\-]{20,}>', handler=RouteHandler),
    webapp2.Route('/route/<action>', handler=RouteHandler),
    webapp2.Route('/route', handler=RouteHandler),
    webapp2.Route('/request/<action>/<key:[\w\-]{20,}>', handler=RequestHandler),
    webapp2.Route('/request/<key:[\w\-]{20,}>', handler=RequestHandler),
    webapp2.Route('/request', handler=RequestHandler),
# reservations
    webapp2.Route('/reserve/<action>/<key:[\w\-]{20,}>', handler=ReservationHandler),
    webapp2.Route('/reserve/<key:[\w\-]{20,}>', handler=ReservationHandler),
# message
    webapp2.Route('/message/<action>/<key:[\w\-]{20,}>', handler=MessageHandler),
# reviews
   webapp2.Route('/review/<action>/<key:[\w\-]{20,}>', handler=ReviewHandler),
   webapp2.Route('/review/<key:[\w\-]{20,}>', handler=ReviewHandler),
   ('/sitemap.xml', SitemapHandler),
   ('/generate/sitemap', SitemapGenerationHandler),
# Utils
   ('/navhead',NavHelper),
   ('/suicide',CloseHelper),
    webapp2.Route('/img/<action>/<sender>/<receiver>', handler=ImageHandler),
# Footer
   ('/about', AboutPage),
   ('/how', HowItWorksPage),
   ('/privacy', PrivacyPage),
   ('/tos', TOSPage),
   ('/jobs', JobsPage),
    webapp2.Route('/blog', handler=BlogPage),
    webapp2.Route('/blog/<post>', handler=BlogPage),
   ('/contact', ContactPage),
# Admin
    webapp2.Route('/test', handler=TestUtils),
    webapp2.Route('/debug/<action>', handler=DebugUtils),
    webapp2.Route('/match/<action>', handler=MatchHandler),
    webapp2.Route('/match/<action>/<key:[\w\-]{20,}>', handler=MatchHandler),
    webapp2.Route('/news/<action>', handler=NewsHandler),
    webapp2.Route('/summary/<action>/<key:[\w\-]{20,}>', handler=SummaryHandler),
   webapp2.Route('/summary', handler=SummaryHandler),
   webapp2.Route('/external/<action>', ExternalHandler),
   webapp2.Route('/admin/<action>', RRDashHandler),
   webapp2.Route('/gerrit/<action>', GerritHandler),
   webapp2.Route('/gerrit/<action>/<loc>', GerritHandler),
   webapp2.Route('/remind/<action>', Reminder),
   webapp2.Route('/notify/<action>/<key>', Notify),
   webapp2.Route('/expire/<action>', ExpireHandler), EmailHandler.mapping()],
  debug=True)

app.error_handlers[400] = ErrorHandler400
app.error_handlers[403] = ErrorHandler403
app.error_handlers[404] = ErrorHandler404
app.error_handlers[409] = ErrorHandler409
app.error_handlers[408] = ErrorHandler408
app.error_handlers[500] = ErrorHandler500
