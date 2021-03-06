import webapp2
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.api import memcache

import logging
import urlparse

import time

from monitor_config import config as monitor_config
import list_handler
import api_handler


class FetchHandler(webapp2.RequestHandler):
	def get(self):
		for cluster_id, cluster_attrs in monitor_config.iteritems():
			taskqueue.add(url='/start_fetch', params={'url': cluster_attrs['url'], 'cluster_id': cluster_id, 'is_list': True})

		self.response.write('start fetching...')

	def post(self):
		url, cluster_id, is_list = self.request.get('url'), self.request.get('cluster_id'), self.request.get('is_list')
		defer_fetch(url, cluster_id, is_list)


def defer_fetch(url, cluster_id, is_list=False):

	logging.info('fetching...%s' % url)

	try:
		result = urlfetch.fetch(url)
		status_code = result.status_code
	except Exception as e:
		if is_list:
			logging.error(e)
			#defer_fetch(url, cluster_id, is_list)
			return
		else:
			logging.error(e)
			#taskqueue.add(url='/start_fetch', params={'url': url, 'cluster_id': cluster_id})
			return
			

	if is_list:
		#cluster_attrs = monitor_config[cluster_id]
		#response_dict = api_handler.getApi(cluster_id)
		#appids = response_dict['B_available']
		appids = list_handler.get_list(cluster_id)
		for appid in appids:
			app_url = 'http://%s.appspot.com/2' % appid
			taskqueue.add(url='/start_fetch', params={'url': app_url, 'cluster_id': cluster_id})
	else:
		appid = urlparse.urlparse(url).netloc.split('.')[0]
		if status_code == 503:
			memcache.set(appid, False, 0, 0, cluster_id)
		else:
			memcache.set(appid, True, 0, 0, cluster_id)

app = webapp2.WSGIApplication([
	('/start_fetch', FetchHandler)
], debug=True)
