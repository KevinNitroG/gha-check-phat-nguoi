from check_phat_nguoi.models.config.plate_info import (
    PlateInfoModel as _PlateInfoConfigModel,
)
from check_phat_nguoi.models.context.violation import ViolationModel
from check_phat_nguoi.utils.constants import DATETIME_STRING_FORMAT
from logging import getLogger
from typing import Dict

from datetime import datetime

logging = getLogger(__name__)


class PlateInfoModel(_PlateInfoConfigModel):
    violation: list[ViolationModel] = []

    def get_plate_info(self, plate: str, plate_violation_dict: Dict | None) -> None:
        self.plate = plate
        if plate_violation_dict is None:
            print("This plate doesn't have any violation")
            logging.info("This plate doesn't have any violation")
            self.violation = None
        else:
            for violation_info_dict in plate_violation_dict["data"]:
                # Handle datetime
                date_string = violation_info_dict["Thời gian vi phạm"]
                date_object: datetime = datetime.strptime(
                    date_string, DATETIME_STRING_FORMAT
                )
                violation_data = {
                    "date": date_object,
                    "location": violation_info_dict["Địa điểm vi phạm"],
                    "action": violation_info_dict["Hành vi vi phạm"],
                    "status": violation_info_dict["Trạng thái"],
                    "enforcement_unit": violation_info_dict["Đơn vị phát hiện vi phạm"],
                    "resolution_office": violation_info_dict["Nơi giải quyết vụ việc"],
                }
                violation_model = ViolationModel(**violation_data)
                self.violation.append(violation_model)


__all__ = ["PlateInfoModel"]
