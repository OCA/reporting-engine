###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Session Store 
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

import json
import pickle
import logging
import functools

from werkzeug.contrib.sessions import SessionStore

from odoo.tools import config

_logger = logging.getLogger(__name__)

try:
    import redis
except ImportError:
    pass

SESSION_TIMEOUT = 60 * 60 * 24 * 7

def retry_redis(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        for attempts in range(1, 6):
            try:
                return func(self, *args, **kwargs)
            except redis.ConnectionError as error:
                _logger.warn("SessionStore connection failed! (%s/5)" % attempts)
                if attempts >= 5:
                    raise error
    return wrapper

class RedisSessionStore(SessionStore):
    
    def __init__(self, *args, **kwargs):
        super(RedisSessionStore, self).__init__(*args, **kwargs)
        self.prefix = config.get('session_store_prefix', '')
        self.server = redis.Redis(
            host=config.get('session_store_host', 'localhost'),
            port=int(config.get('session_store_port', 6379)),
            db=int(config.get('session_store_dbindex', 1)),
            password=config.get('session_store_pass', None)
        )
    
    def _encode_session_key(self, key):
        return key.encode('utf-8') if isinstance(key, str) else key
    
    def _get_session_key(self, sid):
        return self._encode_session_key(self.prefix + sid)
    
    @retry_redis
    def save(self, session):
        key = self._get_session_key(session.sid)
        payload = pickle.dumps(dict(session), pickle.HIGHEST_PROTOCOL)
        self.server.setex(name=key, value=payload, time=SESSION_TIMEOUT)
    
    @retry_redis
    def delete(self, session):
        self.server.delete(self._get_session_key(session.sid))
    
    @retry_redis
    def get(self, sid):
        if not self.is_valid_key(sid):
            return self.new()
        key = self._get_session_key(sid)
        payload = self.server.get(key)
        if payload:
            self.server.setex(name=key, value=payload, time=SESSION_TIMEOUT)
            return self.session_class(pickle.loads(payload), sid, False)
        else:
            return self.session_class({}, sid, False)