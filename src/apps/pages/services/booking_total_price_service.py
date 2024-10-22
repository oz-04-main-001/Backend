from datetime import datetime


class BookingTotalPriceService:

    def __init__(self, price: int, check_in_date: str, check_out_date: str) -> None:
        self.price = price
        self.check_in_date = datetime.strptime(check_in_date, "%Y-%m-%d")
        self.check_out_date = datetime.strptime(check_out_date, "%Y-%m-%d")
        self.total_price = 0

    def calculate_price(self) -> int:
        # 예약 박수 계산
        num_days = (self.check_out_date - self.check_in_date).days

        if num_days > 0:
            self.total_price = self.price * num_days
        else:
            raise ValueError("계산을 할 수 없습니다.")

        return self.total_price

    def __str__(self) -> str:
        # 1000단위로 , 넣어서 출력
        formatted_price = f"{self.total_price:,}"
        return formatted_price
