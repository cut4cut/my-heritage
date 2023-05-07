from typing import List, Tuple

import orjson
import httpx

from heritage.pkg.pastvu.model import GeoPoint, Photo, Params


class PastvuAPI:
    def __init__(self) -> None:
        self._base_url = "https://pastvu.com/api2"
        self._image_url = "https://pastvu.com/_p/d/{0}"

    def get_photo_info(self, cid: str) -> Tuple[str, str]:
        r = httpx.get(
            self._base_url,
            params={"method": "photo.giveForPage", "params": f'{{"cid": {cid}}}'},
        )
        contents = orjson.loads(r.content).get("result", {}).get("photo", {})
        return contents.get("source", ""), contents.get("y", "")

    def get_photo_file(self, file: str) -> bytes:
        r = httpx.get(self._image_url.format(file))
        return r.content

    def get_nearest_photos(self, params: Params) -> List[Photo]:
        r = httpx.get(
            self._base_url,
            params={
                "method": "photo.giveNearestPhotos",
                "params": params.json(models_as_dict=False),
            },
        )

        photos = []
        for data in orjson.loads(r.content).get("result", {}).get("photos", {}):
            source, period = self.get_photo_info(data["cid"])
            photos.append(
                Photo(
                    geo=GeoPoint(latitude=data["geo"][0], longitude=data["geo"][1]),
                    title=data["title"],
                    file_name=data["file"],
                    cid=data["cid"],
                    source=source,
                    period=period,
                )
            )

        return photos
