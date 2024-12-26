CONFIG_PATH: str = "config.json"
SIMPLE_LOG_MESSAGE: str = "[%(levelname)s]: %(message)s"
DETAIL_LOG_MESSAGE: str = (
    "%(asctime)s [%(levelname)s] - %(message)s (%(filename)s:%(lineno)d)"
)

# API from checkphatnguoi.vn
GET_DATA_API_URL_CHECKPHATNGUOI: str = "https://api.checkphatnguoi.vn/phatnguoi"
SEND_MESSAGE_API_URL_TELEGRAM: str = (
    "https://api.telegram.org/bot{bot_token}/sendMessage"
)
DATETIME_FORMAT_CHECKPHATNGUOI: str = "%H:%M, %d/%m/%Y"

OFFICE_NAME_PATTERN = r"^\d+\."

MESSAGE_MARKDOWN_PATTERN = """
*🚗 **Thông tin phương tiện**:*
- **Biển kiểm soát:** `{plate}`
- **Chủ sở hữu:** `{owner}'

*⚠️ **Thông tin vi phạm**:*
- **Hành vi vi phạm:** `{action}`
- **Trạng thái:** {status}
- **Thời gian vi phạm:** `{date}`
- **Địa điểm vi phạm** {location}

*🏢 **Đơn vị phát hiện vi phạm**:*
- **{enforcement_unit}**

*📍 **Nơi giải quyết vụ việc**:*
{resolution_locations}
"""

RESOLUTION_LOCATION_MARKDOWN_PATTERN = """
{idx}. **{location_name}
- **Địa chỉ:** {address}
- **Số điện thoại liên lạc:** {phone}

"""
