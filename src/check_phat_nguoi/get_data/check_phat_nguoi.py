import asyncio
import re
from datetime import datetime
from logging import getLogger
from typing import Dict, override

from aiohttp import ClientConnectionError, ClientSession, ClientTimeout

from check_phat_nguoi.config import PlateInfoDTO
from check_phat_nguoi.context import PlateInfoModel, ViolationModel
from check_phat_nguoi.context.plate_context.models.resolution_office import (
    ResolutionOfficeModel,
)

from ..modules.constants.get_data import (
    DATETIME_FORMAT_CHECKPHATNGUOI as DATETIME_FORMAT,
)
from ..modules.constants.get_data import GET_DATA_API_URL_CHECKPHATNGUOI as API_URL
from ..modules.constants.get_data import OFFICE_NAME_PATTERN
from .get_data_base import GetDataBase

logger = getLogger(__name__)


class GetDataCheckPhatNguoi(GetDataBase):
    def __init__(
        self, plate_infos: tuple[PlateInfoDTO, ...], timeout: int = 10
    ) -> None:
        super().__init__(plate_infos)
        self.data_dict: Dict[PlateInfoDTO, None | Dict] = {}
        self.session = ClientSession()
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}

    async def _get_data_request(self, plate_info_object: PlateInfoDTO) -> None:
        payload: dict[str, str] = {"bienso": plate_info_object.plate}
        try:
            async with self.session.post(
                API_URL,
                headers=self.headers,
                json=payload,
                timeout=ClientTimeout(self.timeout),
            ) as response:
                response.raise_for_status()

                response_data: Dict = await response.json()
                self.data_dict[plate_info_object] = response_data
        except asyncio.TimeoutError:
            logger.error(
                f"Time out of {self.timeout} seconds from URL {API_URL} for plate: {plate_info_object.plate}"
            )
        except ClientConnectionError:
            logger.error(
                f"Error occurs while connecting to {API_URL} for plate: {plate_info_object.plate}"
            )

    async def _get_data(self) -> None:
        tasks = [self._get_data_request(plate_info) for plate_info in self._plate_infos]
        await asyncio.gather(*tasks)

    @staticmethod
    def get_plate_violation(
        plate_violation_dict: Dict | None,
    ) -> tuple[ViolationModel, ...]:
        if plate_violation_dict is None:
            return ()

        def _create_resolution_office_mode(
            resolution_offices: list[str],
        ) -> tuple[ResolutionOfficeModel, ...]:
            parsed_office_dict: Dict[str, Dict] = {}
            current_name = None
            for office_info in resolution_offices:
                if re.match(OFFICE_NAME_PATTERN, office_info):
                    current_name = office_info.split(".", 1)[1].strip()
                    parsed_office_dict[current_name] = {"Address": None, "Phone": None}
                elif "Địa chỉ" in office_info:
                    if current_name:
                        parsed_office_dict[current_name]["Address"] = office_info.split(
                            ":", 1
                        )[1].strip()
                elif "Số điện thoại" in office_info:
                    if current_name:
                        parsed_office_dict[current_name]["Phone"] = office_info.split(
                            ":", 1
                        )[1].strip()

            return tuple(
                ResolutionOfficeModel(
                    location_name=location_name,
                    address=location_detail["Address"],
                    phone=location_detail["Phone"],
                )
                for location_name, location_detail in parsed_office_dict.items()
            )

        def _create_violation_model(data: Dict):
            return ViolationModel(
                type=data["Loại phương tiện"],
                date=datetime.strptime(data["Thời gian vi phạm"], DATETIME_FORMAT),
                location=data["Địa điểm vi phạm"],
                action=data["Hành vi vi phạm"],
                status=data["Trạng thái"],
                enforcement_unit=data["Đơn vị phát hiện vi phạm"],
                resolution_office=_create_resolution_office_mode(
                    data["Nơi giải quyết vụ việc"]
                ),
            )

        return tuple(
            _create_violation_model(violation_info_dict)
            for violation_info_dict in plate_violation_dict["data"]
        )

    @override
    async def get_data(self) -> tuple[PlateInfoModel, ...]:
        await self._get_data()
        plate_infos: tuple[PlateInfoModel, ...] = tuple(
            PlateInfoModel(
                plate=plate_info_object.plate,
                owner=plate_info_object.owner,
                violation=GetDataCheckPhatNguoi.get_plate_violation(
                    plate_violation_dict=plate_violation_dict
                ),
            )
            for plate_info_object, plate_violation_dict in self.data_dict.items()
        )
        await self.session.close()

        return plate_infos