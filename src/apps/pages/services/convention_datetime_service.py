from datetime import datetime
from typing import Dict, Optional


class ConventionDateService:
    @staticmethod
    def format_datetime(datetime_str: str) -> Optional[str]:
        """Format the input datetime string to 'YYYY-MM-DD'."""
        try:
            # Parse the datetime string into a datetime object
            dt = datetime.fromisoformat(datetime_str)
            # Return formatted date as string in 'YYYY-MM-DD'
            return dt.strftime("%Y-%m-%d")  # 'YYYY-MM-DD' 형식으로 반환
        except ValueError:
            return None  # 유효하지 않은 datetime 문자열인 경우 None 반환

    @staticmethod
    def format_dates(data: Dict[str, str]) -> Dict[str, str]:
        """Format 'check_in_datetime' and 'check_out_datetime' in the given dictionary."""
        formatted_data = {}
        for key, value in data.items():
            if key in ["check_in_datetime", "check_out_datetime"]:
                formatted_data[key] = ConventionDateService.format_datetime(value)
        return formatted_data
