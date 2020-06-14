"""Support for powering relays in a DoorBird video doorbell."""
import datetime
import logging

try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity

import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .entity import PIKIntercomEntity

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    acc = hass.data[DOMAIN]['account'].account
    intercoms = []
    entities = []
    for apart in acc.apartments():
        intercoms.extend(apart.intercoms())

    for i in intercoms:
        entities.append(
            PIKIntercomSwitch(
                i,
            )
        )

    add_entities(entities)


class PIKIntercomSwitch(PIKIntercomEntity, SwitchEntity):
    """PIKIntercom device."""

    def __init__(self, intercom):
        """Initialize PIKIntercom device."""
        super().__init__(intercom)
        self._intercom = intercom
        self._state = False
        self._assume_off = datetime.datetime.min

        self._time = datetime.timedelta(seconds=5)
        self._unique_id = f"{self._intercom.id()}"

    @property
    def unique_id(self):
        """Switch unique id."""
        return self._unique_id

    @property
    def icon(self):
        """Return the icon to display."""
        return "mdi:dip-switch"

    @property
    def is_on(self):
        """Get the assumed state of the relay."""
        return self._state

    def turn_on(self, **kwargs):
        """Open intercom"""
        result = self._intercom.open()
        if not result:
            raise Exception("failed")
        _LOGGER.info(f'Door {str(self._intercom)} open')

        now = dt_util.utcnow()
        self._assume_off = now + self._time

    def turn_off(self, **kwargs):
        """Turn off the relays is not needed. They are time-based."""
        raise NotImplementedError("PIKIntercom cannot be manually turned off.")

    def update(self):
        """Wait for the correct amount of assumed time to pass."""
        if self._state and self._assume_off <= dt_util.utcnow():
            self._state = False
            self._assume_off = datetime.datetime.min
    
    @property
    def model(self):
        return "switch"
