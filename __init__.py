"""The Intercom PIK integration. Private only usage"""
import logging
import threading

import voluptuous as vol

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_DEV_ID, CONF_LOGIN, CONF_PASSWORD

from .pik_intercom_api.obj import Account

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_LOGIN): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Optional(CONF_DEV_ID): str,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.All(cv.ensure_list, [DEVICE_SCHEMA])},
    extra=vol.ALLOW_EXTRA)

PLATFORMS = ["switch", "camera"]

_LOGGER = logging.getLogger(__name__)


def setup(hass: HomeAssistant, config: dict):
    """Set up the Intercom PIK component."""
    conf = config.get(DOMAIN)
    if len(conf) != 1:
        raise Exception("only one intercom supported")

    login = conf[0].get(CONF_LOGIN)
    password = conf[0].get(CONF_PASSWORD)
    dev_id = conf[0].get(CONF_DEV_ID)

    hass.data[DOMAIN] = {'account': PIKIntercomAccount(login, password, dev_id)}

    return True

class PIKIntercomAccount:

    def __init__(self, login, password, dev_id, update_interval=60):
        self.__account = Account(login, password, dev_id)
        self.__update_interval=update_interval
        self.activity_loop()
    
    @property
    def account(self):
        return self.__account

    def activity_loop(self):
        self.__account.last_open()
        threading.Timer(self.__update_interval, self.activity_loop).start()
