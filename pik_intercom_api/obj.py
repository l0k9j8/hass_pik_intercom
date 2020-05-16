from .api import API


class Account:
    def __init__(self, login, password, device_id):
        self._api = API(login, password, device_id)

    def apartments(self):
        aparts = []
        for k, v in self._api.apartments().items():
            aparts.append(Apartment(self, v))
        return aparts


class Apartment:
    def __init__(self, account, apart_dict):
        self.__account = account
        self.__id = apart_dict['id']
        self.__building_id = apart_dict['building_id']
        self.__room_number = apart_dict['number']
        self.__init_building()

    def __init_building(self):
        building = self.__account._api.building(self.__building_id)
        self.__house = building.get('house', '')
        self.__street = building.get('street', '')
        self.__location = building.get('location', ['', ''])
        self.__management_company = building.get('management_company', {})

    def account(self):
        return self.__account

    def intercoms(self):
        api_intercoms = self.__account._api.intercoms(self.__id)
        result = []
        for k, v in api_intercoms.items():
            result.append(Intercom(self, v))
        return result

    def __str__(self):
        return f'{self.__street} {self.__house} {self.__room_number}'

    def __repr__(self):
        return f'Apartment obj ({self.__id}): {self.__street} {self.__house} {self.__room_number}'


class Intercom:

    def __init__(self, apartment, intercom_dict):
        self.__apartment = apartment
        self.__id = intercom_dict['id']
        self.__mode = intercom_dict['mode']
        self.__photo = intercom_dict.get('photo_url', None)
        self.__video = []
        if intercom_dict['video'] is not None:
            for video in intercom_dict['video']:
                self.__video.append({'quality': video['quality'],
                                     'src': video['source']})

        if intercom_dict['sip_account'] is not None:
            self.__sip = {
                'enable': intercom_dict['sip_account']['ex_enable'],
                'user': intercom_dict['sip_account']['ex_user'],
                'password': intercom_dict['sip_account']['password'],
                'proxy': intercom_dict['sip_account']['proxy'],
            }
        else:
            self.__sip = {}

        self.__entrance = intercom_dict['entrance']

        if intercom_dict['renamed_name'] != '':
            self.__name = intercom_dict['renamed_name']
        else:
            self.__name = intercom_dict['human_name']

    def id(self):
        return self.__id

    def name(self):
        return self.__name

    def open(self):
        return self.__apartment.account()._api.open_intercom(self.__id, self.__mode)

    def photo(self):
        if len(self.__photo) == 0:
            return None
        return self.__photo

    def video(self, quality=None):
        for v in self.__video:
            if quality is None:
                return v['src']
            else:
                if quality == v['quality']:
                    return v['src']
        if len(self.__video) > 0:
            return self.__video[0]['src']

    def __str__(self):
        return f'{str(self.__apartment)}: {self.__name}'

    def __repr__(self):
        return f'Intercom obj ({self.__id}): {str(self)}'
