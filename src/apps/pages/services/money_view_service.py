# 1000단위 , 찍기
class MoneyViewService:
    @staticmethod
    def format(price: int) -> str:
        return f"{price:,}"
