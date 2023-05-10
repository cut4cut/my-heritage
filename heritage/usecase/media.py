from typing import List

from heritage.exc import NoPhotos
from heritage.entity import MediaPhoto
from heritage.pkg import Params, PastvuAPI, GeoPoint


class MediaGroupUseCase:
    def __init__(self, api: PastvuAPI) -> None:
        self.api = api

    def get_photos(
        self, latitude: float, longitude: float, page: int = 0
    ) -> List[MediaPhoto]:
        parapms = Params(
            geo=GeoPoint(
                latitude=latitude,
                longitude=longitude
            )
        ).set_pagination(page)
        group = []
        for photo in self.api.get_nearest_photos(parapms):
            file = self.api.get_photo_file(photo.file_name)
            group.append(
                MediaPhoto(
                    file=file,
                    title=photo.title,
                    period=photo.period,
                )
            )

        if group:
            return group

        raise NoPhotos
