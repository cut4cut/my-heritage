from typing import List, Tuple

import orjson
import httpx

from heritage.pkg.pastvu.models import GeoPoint, Photo, Params


class PastvuAPI:
    def __init__(self) -> None:
        self.base_url = "https://pastvu.com/api2"

    def get_photo_info(self, cid: str) -> Tuple[str, str]:
        r = httpx.get(
            self.base_url,
            params={"method": "photo.giveForPage", "params": f'{{"cid": {cid}}}'},
        )
        contents = orjson.loads(r.content).get("result", {}).get("photo", {})
        return contents.get("source", ""), contents.get("y", "")

    def get_nearest_photos(self, params: Params) -> List[Photo]:
        r = httpx.get(
            self.base_url,
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
                    file=data["file"],
                    cid=data["cid"],
                    source=source,
                    period=period,
                )
            )

        return photos


def main():
    p = Params()
    print(p)
    api = PastvuAPI()
    for photo in api.get_nearest_photos(p):
        print(photo)

    print()


if __name__ == "__main__":
    main()
