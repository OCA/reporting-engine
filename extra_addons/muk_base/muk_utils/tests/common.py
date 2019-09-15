###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Utils 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import os
import time
import hmac
import hashlib
import logging
import functools
import threading
import traceback

from odoo.tests import common, HOST, PORT

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# Decorators
#----------------------------------------------------------

def multi_users(users=[['base.user_root', True], ['base.user_admin', True]], reset=True, raise_exception=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            user_list = users(self) if callable(users) else users
            test_results = []
            for user in user_list:
                self.cr.execute('SAVEPOINT test_multi_users')
                try:
                    if not isinstance(user[0], int):
                        self.uid = self.ref(user[0])
                    else:
                        self.uid = user[0]
                    func(self, *args, **kwargs)
                except Exception as error:
                    test_results.append({
                        'user': user[0], 
                        'expect': user[1],
                        'result': False,
                        'error': error,
                    })
                else:
                    test_results.append({
                        'user': user[0], 
                        'expect': user[1],
                        'result': True,
                        'error': None,
                    })
                if reset:
                    self.env.cache.invalidate()
                    self.registry.clear_caches()
                    self.registry.reset_changes()
                    self.cr.execute('ROLLBACK TO SAVEPOINT test_multi_users')
                else:
                    self._cr.execute('RELEASE SAVEPOINT test_multi_users')
            test_fails = []
            for result in test_results:
                if result['expect'] != result['result']:
                    message = "Test (%s) with user (%s) failed!"
                    _logger.info(message % (func.__name__, result['user']))
                    if result['error']:
                        _logger.error(result['error'], exc_info=True)
                    test_fails.append(result)
            if test_fails:
                message = "%s out of %s tests failed" % (len(test_fails), len(test_results))
                if raise_exception:
                    raise test_fails[0]['error']
                else:
                    _logger.info(message)
            return test_results
        return wrapper
    return decorator

def track_function(max_query_count=None, max_query_time=None, max_time=None, return_tracking=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracking_parameters = [func.__name__]
            threading.current_thread().query_time = 0
            threading.current_thread().query_count = 0
            threading.current_thread().perf_t0 = time.time()
            result = func(*args, **kwargs)
            message = "%s" % func.__name__
            if args and hasattr(args[0], "uid"):
                message = " (%s)" % args[0].uid
            if hasattr(threading.current_thread(), "query_count"):
                query_count = threading.current_thread().query_count
                query_time = threading.current_thread().query_time
                perf_t0 = threading.current_thread().perf_t0
                remaining_time = time.time() - perf_t0 - query_time
                time_taken = query_time + remaining_time
                message += " - %s Q %.3fs QT %.3fs OT %.3fs TT" % (
                    query_count, query_time, remaining_time, time_taken
                )
                tracking_parameters += [
                    query_count, query_time, remaining_time, time_taken
                ]
                if max_query_count and query_count > max_query_count:
                    raise AssertionError("More than %s queries" % max_query_count)
                if max_query_time and query_time > max_query_time:
                    raise AssertionError("Queries took longer than %.3fs" % max_query_time)
                if max_time and time_taken > max_time:
                    raise AssertionError("Function took longer than %.3fs" % max_time)
            if not return_tracking:
                _logger.info(message)
            if return_tracking:
                return result, tracking_parameters
            return result
        return wrapper
    return decorator

#----------------------------------------------------------
# Test Cases
#----------------------------------------------------------

class HttpCase(common.HttpCase):
    
    def csrf_token(self, time_limit=3600):
        token = self.session.sid
        max_ts = '' if not time_limit else int(time.time() + time_limit)
        msg = '%s%s' % (token, max_ts)
        secret = self.env['ir.config_parameter'].sudo().get_param('database.secret')
        assert secret, "CSRF protection requires a configured database secret"
        hm = hmac.new(secret.encode('ascii'), msg.encode('utf-8'), hashlib.sha1).hexdigest()
        return '%so%s' % (hm, max_ts)
    
    def url_open(self, url, data=None, timeout=10, csrf=False):
        if url.startswith('/'):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        if data:
            if csrf:
                data.update({'csrf_token': self.csrf_token()})
            return self.opener.post(url, data=data, timeout=timeout)
        return self.opener.get(url, timeout=timeout)
    
    