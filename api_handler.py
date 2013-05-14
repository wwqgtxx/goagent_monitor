# coding: utf-8

import webapp2
from google.appengine.api import urlfetch
from google.appengine.api import memcache


import json


from fetch_config import config as fetch_config

class ApiHandler(webapp2.RequestHandler):
    def get(self, cluster_id=None):
        cluster_attrs = fetch_config[cluster_id]

        result = urlfetch.fetch(cluster_attrs['url'])
        appids = result.content.split('|')

        mem_appids = memcache.get_multi(appids)

        response_dict = {
            "available": [],
            "over_quota": [],
        }

        for appid in mem_appids:
            if bool(appid) == True:
                response_dict['available'].append(appid)
            elif bool(appid) == False:
                response_dict['over_quota'].append(appid)

        response_dict['available_str'] = "今日还剩 %d GB/%d GB 流量" % (len(response_dict['available']), len(mem_appids))

        response_json = json.dumps(response_dict, ensure_ascii=False)

        self.response.write(response_json)







app = webapp2.WSGIApplication([
    # (r'/api', ApiHandler),
    (r'/api/(.*)', ApiHandler)
], debug=True)