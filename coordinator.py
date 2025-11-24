import logging
from datetime import datetime, timedelta

import aiohttp
import xml.etree.ElementTree as ET

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class Frank2Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, token, domain, inkoop, eb, btw):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(hours=1))
        self.token = token
        self.domain = domain
        self.inkoop = inkoop
        self.eb = eb
        self.btw = btw

    async def _async_update_data(self):
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        data = {}
        ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3'}
        for date in [today, tomorrow]:
            date_str = date.strftime("%Y%m%d")
            next_date_str = (date + timedelta(days=1)).strftime("%Y%m%d")
            url = f"https://web-api.tp.entsoe.eu/api?securityToken={self.token}&documentType=A44&in_Domain={self.domain}&out_Domain={self.domain}&periodStart={date_str}0000&periodEnd={next_date_str}0000"
            try:
                _LOGGER.debug(f"Fetching data for {date_str} from {url}")
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        _LOGGER.debug(f"Response status for {date_str}: {resp.status}")
                        if resp.status != 200:
                            _LOGGER.warning(f"Failed to fetch data for {date_str}: {resp.status}")
                            continue
                        xml = await resp.text()
                _LOGGER.debug(f"XML received for {date_str}: {xml[:500]}...")  # Log first 500 chars
                root = ET.fromstring(xml)
                time_series = root.find(".//ns:TimeSeries", ns)
                if time_series is None:
                    _LOGGER.debug(f"No TimeSeries found in XML for {date_str}")
                    continue
                time_interval = time_series.find(".//ns:timeInterval", ns)
                if time_interval is None:
                    _LOGGER.debug(f"No timeInterval found in XML for {date_str}")
                    continue
                start = time_interval.find("ns:start", ns).text
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                points = []
                for point in time_series.findall(".//ns:Point", ns):
                    position = int(point.find("ns:position", ns).text)
                    price_elem = point.find("ns:price.amount", ns)
                    if price_elem is None:
                        continue
                    price = float(price_elem.text)
                    minutes = (position - 1) * 15
                    start_time = start_dt + timedelta(minutes=minutes)
                    end_time = start_time + timedelta(minutes=15)
                    price_kwh = price / 1000
                    allin = (price_kwh + self.inkoop) * (1 + self.btw / 100) + self.eb
                    local_tz = dt_util.get_default_time_zone()
                    start_dt_local = dt_util.as_local(start_time)
                    end_dt_local = dt_util.as_local(end_time)
                    points.append({
                        "start": start_dt_local.isoformat(),
                        "end": end_dt_local.isoformat(),
                        "price": round(allin, 5),
                        "net_price": round(price_kwh, 5)
                    })
                _LOGGER.debug(f"Found {len(points)} points for {date_str}")
                data[date_str] = points
            except Exception as e:
                _LOGGER.error(f"Error fetching data for {date_str}: {e}")
        _LOGGER.debug(f"Final data: {data}")
        return data