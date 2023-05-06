
from dataclasses import dataclass

import orjson
import httpx
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class GeoPoint(BaseModel):
    latitude: float = 55.724322
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
    file: str
    cid: int

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        json_encoders = {
            GeoPoint: lambda g: [g.latitude, g.longitude],
        }



def main():

    p = Params()
    print(p)

    r = httpx.get("https://pastvu.com/api2", params={
        "method": "photo.giveNearestPhotos",
        "params": p.json(models_as_dict=False)
    })


    contents = orjson.loads(r.content) 

    for idx, data in enumerate(contents.get("result", {}).get("photos", {})):
        #print(idx, photo)
        photo = Photo(
            geo=GeoPoint(latitude=data["geo"][0], longitude=data["geo"][1]),
            title=data["title"],
            file=data["file"],
            cid=data["cid"]
        )
        print(photo)

        r = httpx.get("https://pastvu.com/api2", params={
            "method": "photo.giveForPage",
            "params": f'{{"cid": {photo.cid}}}'
        })
        contents = orjson.loads(r.content) 
        print(contents)
        break


    print()


if __name__ == "__main__":
    main()
