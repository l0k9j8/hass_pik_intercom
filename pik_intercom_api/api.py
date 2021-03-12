#!/usr/bin/env python
import os
import json
import uuid

from requests import Request, Session

from urllib.parse import urljoin, urlencode

API_VERSION = '2'
API_HOST = "https://intercom.pik-comfort.ru/api/"
TIMEOUT = 60


DEVICES = ""


class API:

    def __init__(self, login, password, dev_id=None):
        self.__login = login
        self.__password = password
        if dev_id is None:
            self.__dev_id = uuid.uuid1()
        else:
            self.__dev_id = dev_id
        self.__session = Session()
        self.__header_map = {'api-version': API_VERSION}
        self.__init_session()

    def __send_request(self, method, path, data):
        url = urljoin(API_HOST, path)
        req = Request(method, url,
                      headers=self.__header_map,
                      data=data)

        resp = self.__session.send(req.prepare())

        if resp.status_code != 200:
            raise Exception(
                f"Bad response: {resp.status_code}\nURL: {url}\nBody:{resp.text}")
        auth = resp.headers.get('authorization')
        if auth:
            self.__header_map['authorization'] = auth
        return resp.json()

    def __init_session(self):
        sign_in_url = "customers/sign_in"
        data = self.__send_request('POST', sign_in_url,
                                   {
                                       'account[password]': self.__password,
                                       'account[phone]': self.__login,
                                       'customer_device[uid]': self.__dev_id,
                                   })
        self.__account = data.get('account')
        self.__devices = data.get('customer_devices')

    def apartments(self):
        properties_url = 'customers/properties'
        data = self.__send_request('GET', properties_url, None)
        apartments = {}
        for item in data.get('apartments', []):
            apartments[item['id']] = item
        for item in data.get('parking_places', []):
            apartments[item['id']] = item
        for item in data.get('storerooms', []):
            apartments[item['id']] = item
        return apartments

    def building(self, building_id):
        home_url = f'buildings/{building_id}'
        data = self.__send_request('GET', home_url, None)
        apartments = {}
        return data

    def intercoms(self, apartment_id):
        intercoms_url = f'customers/properties/{apartment_id}/intercoms'
        data = self.__send_request('GET', intercoms_url, None)
        intercoms = {}
        for item in data:
            intercoms[item['id']] = item
        return intercoms

    def open_intercom(self, intercom_id, intercom_mode):
        open_intercoms_url = f'customers/intercoms/{intercom_id}/unlock'
        data = self.__send_request('POST', open_intercoms_url,
                                   {
                                       'door': intercom_mode,
                                       'id': intercom_id,
                                   }
                                   )
        return data.get('request', False)

    def last_open(self):
        last_open_intercoms_url = f'call_sessions/last_open'
        data = self.__send_request('GET', last_open_intercoms_url, None)
        return data
