resreceipt_txt = """
        Thank you for your reservation with Barnacle.\n
        If you have any questions or schedule changes, please contact us at 
        help@gobarnacle.com.\n\n
        You can access your reservation at any time by going to http://www.gobarnacle.com/account\n\n\n
        Reservation Details\n\n
        Origin:  %(locstart)s\n
        %(dropoffstr)s\n
        Destination: %(locend)s\n
        %(pickupstr)s\n
        %(delivby)s\n\n
        Driver: %(first_name)s
        %(ins_email)s\n\n
        Total: $%(rates)d
"""

resreceipt_anon = """
        Thank you for your reservation with Barnacle.\n
        If you have any questions or schedule changes, please contact us at 
        help@gobarnacle.com.\n\n
        Reservation Details\n\n
        Origin:  %(locstart)s\n
        Destination: %(locend)s\n
        %(delivby)s\n\n
        Total: $%(rates)d
"""

receipt_txt = """
        Thank you for your reservation with Barnacle.\n
        If you have any questions or schedule changes, please contact us at 
        help@gobarnacle.com.\n\n
        You can access your reservation at any time by going to http://www.gobarnacle.com/account\n\n\n
        Reservation Details\n\n
        Origin:  %(locstart)s\n
        %(delivstart)s\n
        Destination: %(locend)s\n
        %(delivend)s%(delivby)s\n\n
        Driver: %(first_name)s
        %(ins_email)s\n\n
        Special instructions: %(details)s\n\n
        Total: $%(rates)d
"""

welcome_txt = """
        Thank you for signing up to become a driver. It's easy to get on the road and making deliveries. \n
        Here are some things you can do to get started.\n\n
        Set up a payment account\n
        Barnacle users appreciate the added security of our escrow system. Have your payments securely transferred to your bank account and funds will be released upon delivery confirmation.\n
        Do that here: http://www.gobarnacle.com/settings\n\n
        Post a driving route\n
        Add your next drive to our database so that other users can find you when they need to send something!\n
        Do that here: http://www.gobarnacle.com/drive\n\n
        Search for requests\n
        If you don't have a planned travel itinerary, search our user requests.\n
        Do that here: http://www.gobarnacle.com/search/request\n\n
        An in-depth guide to getting started is available for you at http://www.gobarnacle.com/profile/drivestart \n\n
        If you ever have any questions, feel free to contact us at 
        help@gobarnacle.com and we will respond within a day!
"""

requestnote_txt = """
        Barnacle users have requested deliveries along your route! You can make a delivery offer on their request page.\n\n
        %(posts)s\n\n
        Change your notification settings and view your routes by going to your account page: http://www.gobarnacle.com/account.
"""

routenote_txt = """
        Barnacle drivers have posted routes that match your request! You can make a reservation on their route page.\n\n
        %(posts)s\n\n
        Change your notification settings and view your requests by going to your account page: http://www.gobarnacle.com/account.
"""

sharetrack_txt = """
        %(first_name)s has shared a route with you\n\n
        Track %(first_name)s\'s progress in real time with the Barnacle Driver Tracker.\n\n 
        %(first_name)s\'s Tracking Page: %(url)s
"""

msgwall_txt = """
        You have a new message\n\n
        There is a new message on your page. Click the link below to view and reply to your message.\n\n
        http://www.gobarnacle.com%(url)s
"""        

complreq_txt = """
        Dear %(first_name)s,\n\n
        You recently started a request to ship through Barnacle.  We would like to advertise this to our fleet of drivers, but we need you to complete your request.  You can finish where you left off at http://www.gobarnacle.com%(req_url)s.\n\n

        Every day, we are proud to help people like you ship goods affordably with our friendly network of drivers.  If you have any questions about best practices in shipping through Barnacle, please don't hesitate to reply directly to this email.\n\n
"""


addcc_txt = """
        Dear %(first_name)s,\n\n
        You recently posted a request to ship through Barnacle.  We will advertise this to our fleet of drivers as soon as you add a valid credit card to your account.  You can do so here: https://www.gobarnacle.com/account.\n\n

        As a reminder, you will not be charged until a driver accepts your request, and the payment will not be released to the driver until you confirm delivery. If you have any questions, please reply directly to this email.\n\n
"""