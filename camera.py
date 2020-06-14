"""Support for viewing the camera feed from a DoorBird video doorbell."""
import datetime
import logging

import aiohttp
import asyncio
import async_timeout

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .entity import PIKIntercomEntity


_LIVE_INTERVAL = datetime.timedelta(seconds=45)
_LOGGER = logging.getLogger(__name__)
_TIMEOUT = 15  # seconds
RTSP_TRANSPORT = "rtsp_transport"

# pik domofon hack
RTSP_TRANS_PROTOCOL = "tcp"


def setup_platform(hass, config, add_entities, discovery_info=None):
    acc = hass.data[DOMAIN]['account'].account
    intercoms = []
    entities = []
    for apart in acc.apartments():
        intercoms.extend(apart.intercoms())

    for i in intercoms:
        if i.video():
            entities.append(
                PIKIntercomCamera(
                    i,
                )
            )

    add_entities(entities)


class PIKIntercomCamera(PIKIntercomEntity, Camera):
    """The camera on a PIK Intercom device."""

    def __init__(
        self,
        pik_intercom,
        interval=None,
    ):
        """Initialize the camera on a PIKIntercom  device."""
        super().__init__(pik_intercom)
        self._stream_url = pik_intercom.video()
        self.stream_options = {RTSP_TRANSPORT: RTSP_TRANS_PROTOCOL}
        self._last_image = None
        self.is_streaming = True
        self._supported_features = SUPPORT_STREAM if self._stream_url else 0
        self._interval = interval or datetime.timedelta
        self._last_update = datetime.datetime.min
        self._unique_id = f"{pik_intercom.id()}"

    async def stream_source(self):
        """Return the stream source."""
        return self._stream_url

    @property
    def unique_id(self):
        """Camera Unique id."""
        return self._unique_id

    @property
    def supported_features(self):
        """Return supported features."""
        return self._supported_features

    async def async_camera_image(self):
        """Pull a still image from the camera."""
        try:
            websession = async_get_clientsession(self.hass)
            with async_timeout.timeout(_TIMEOUT):
                response = await websession.get(self._intercom.photo())

            self._last_image = await response.read()
            return self._last_image
        except asyncio.TimeoutError:
            _LOGGER.error("PIKIntercom %s: Camera image timed out", self._name)
            return self._last_image
        except aiohttp.ClientError as error:
            _LOGGER.error(
                "PIKIntercom %s: Error getting camera image: %s", self._name, error
            )
            return self._last_image
    
    @property
    def model(self):
        return "camera"
