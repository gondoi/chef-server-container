# Copyright (c) 2011-2014 Rackspace Hosting
# All Rights Reserved.
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Chef server routes."""

import datetime
import logging

import bottle
import chef
from chef import auth as chef_auth
import requests

LOG = logging.getLogger(__name__)
IGNORE_HEADERS = (
    'content-length',
    'connection',
    'transfer-encoding',
    'content-encoding',
    'status',
)


class Chef(chef.ChefAPI):

    """Extra function to work with Chef API."""

    def get_headers(self, method, path, headers={}, data=None):
        """Use pychef functions to generate chef request headers."""
        auth_headers = chef_auth.sign_request(
            key=self.key, http_method=method, path=path, body=data,
            host='localhost',
            timestamp=datetime.datetime.utcnow(), user_id=self.client
        )
        request_headers = {}
        request_headers.update(self.headers)
        request_headers.update(dict((k.lower(), v)
                                    for k, v in headers.iteritems()))
        request_headers['x-chef-version'] = self.version
        request_headers.update(auth_headers)

        return request_headers

    def requests_object(self, method, path, headers={}, data=None):
        """Get requests object with headers generated using pychef funcs."""
        headers = self.get_headers(method, path, headers, data)
        url = self.url + path
        response = requests.request(method, url, headers=headers, data=data,
                                    verify=False)
        if response.ok:
            return response
        else:
            response.raise_for_status()


class Router(object):

    """REST API proxy for Chef."""

    def __init__(self, app):
        self.url = 'https://localhost/'
        self.key = '/etc/chef-server/admin.pem'
        self.client = 'admin'

        self.app = app
        app.route('/validation_key', 'GET', self.chef_validator_key)
        app.route('<path:re:.*>',
                  ['GET', 'POST', 'PUT', 'DELETE'],
                  self.chef_request)

    def chef_validator_key(self):
        with open('/etc/chef-server/chef-validator.pem') as validator_key:
            return validator_key.readlines()

    def chef_request(self, path=None):
        """Pass all chef API requests through to local chef in container."""
        request = bottle.request
        print bottle.request.body.readlines()
        api = Chef(self.url, self.key, self.client)

        headers = {
            'accept': request.headers['accept'],
            'content-type': request.headers['content-type'],
        }
        try:
            response = api.requests_object(request.method, path,
                                           data=request.body.getvalue(),
                                           headers=headers)
        except requests.HTTPError as error:
            bottle.response.status = error.response.status_code
            return error.response.content

        bottle.response.status = response.status_code
        for header in response.headers:
            if header not in IGNORE_HEADERS:
                bottle.response.set_header(header, response.headers[header])
        return response.content


if __name__ == "__main__":
    Router(bottle.default_app())
    bottle.run(host='0.0.0.0', port=8888, reloader=True)
