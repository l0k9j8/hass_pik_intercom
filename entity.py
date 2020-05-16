"""The Pik intercoms integration base entity."""
import logging

from homeassistant.helpers.entity import Entity

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