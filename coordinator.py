import logging
from datetime import datetime, timedelta

import aiohttp
import xml.etree.ElementTree as ET

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class Frank2Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, token, domain, inkoop, eb):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(hours=1))
        self.token = token
        self.domain = domain
        self.inkoop = inkoop
        self.eb = eb

    async def _async_update_data(self):
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        data = {}
        ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0'}
        for date in [today, tomorrow]:
            date_str = date.strftime("%Y%m%d")
            url = f"https://web-api.tp.entsoe.eu/api?securityToken={self.token}&documentType=A44&in_Domain={self.domain}&out_Domain={self.domain}&periodStart={date_str}0000&periodEnd={date_str}2300"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            _LOGGER.warning(f"Failed to fetch data for {date_str}: {resp.status}")
                            continue
                        xml = await resp.text()
                root = ET.fromstring(xml)
                time_interval = root.find(".//ns:timeInterval", ns)
                if time_interval is None:
                    continue
                start = time_interval.find("ns:start", ns).text
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                points = []
                for point in root.findall(".//ns:Point", ns):
                    position = int(point.find("ns:position", ns).text)
                    price_elem = point.find("ns:price.amount", ns)
                    if price_elem is None:
                        continue
                    price = float(price_elem.text)
                    minutes = (position - 1) * 15
                    start_time = start_dt + timedelta(minutes=minutes)
                    end_time = start_time + timedelta(minutes=15)
                    price_kwh = price / 1000
                    allin = price_kwh + self.inkoop + self.eb
                    points.append({
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "price": round(allin, 5)
                    })
                data[date_str] = points
            except Exception as e:
                _LOGGER.error(f"Error fetching data for {date_str}: {e}")
        return data