"""The Pik intercoms integration base entity."""
import logging

from homeassistant.helpers.entity import Entity

from .const import DOMAIN, MANUFACTURE

_LOGGER = logging.getLogger(__name__)


class PIKIntercomEntity(Entity):
    """Base class for pik intercom entities."""

    def __init__(self, pik_intercom):
        """Initialize the entity."""
        super().__init__()
        self._intercom = pik_intercom

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self._intercom.name()}"
    
    @property
    def device_info(self):
        dev_info = {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.unique_id)
            },
            "name": self.name,
            "manufacturer": MANUFACTURE,
            "model": self.model,
            "sw_version": "0.0.1",
        }
        return dev_info