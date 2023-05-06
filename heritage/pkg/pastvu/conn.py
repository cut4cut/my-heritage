from typing import List, Tuple

import orjson
import httpx
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class GeoPoint(BaseModel):
    latitude: float = 55.824322
    longitude: float = 37.611089


class Params(BaseModel):
    geo: GeoPoint = GeoPoint()
    limit: int = 3
    skip: int = 0

    def next(self) -> None:
        self.skip += self.limit

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        json_encoders = {
            GeoPoint: lambda g: [g.latitude, g.longitude],
        }


class Photo(BaseModel):
    geo: GeoPoint
    title: str
    source: str
    period: str
    file: str
    cid: int


class PastvuAPI:
    def __init__(self) -> None:
        self.base_url = "https://pastvu.com/api2"

    def get_photo_info(self, cid: str) -> Tuple[str, str]:
        r = httpx.get(
            self.base_url,
            params={"method": "photo.giveForPage",
                    "params": f'{{"cid": {cid}}}'},
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
                    geo=GeoPoint(
                        latitude=data["geo"][0],
                        longitude=data["geo"][1]
                    ),
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

    r = httpx.get(
        "https://pastvu.com/api2",
        params={
            "method": "photo.giveNearestPhotos",
            "params": p.json(models_as_dict=False),
        },
    )

    contents = orjson.loads(r.content)

    for idx, data in enumerate(contents.get("result", {}).get("photos", {})):
        # print(idx, photo)
        photo = Photo(
            geo=GeoPoint(latitude=data["geo"][0], longitude=data["geo"][1]),
            title=data["title"],
            file=data["file"],
            cid=data["cid"],
        )
        print(photo)

        r = httpx.get(
            "https://pastvu.com/api2",
            params={"method": "photo.giveForPage",
                    "params": f'{{"cid": {photo.cid}}}'},
        )
        contents = orjson.loads(r.content).get("result", {}).get("photo", {})
        print(contents)
        print(contents["source"], contents["y"])
        break

    print()


if __name__ == "__main__":
    main()
