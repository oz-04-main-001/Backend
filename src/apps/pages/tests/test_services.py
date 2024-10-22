from unittest import TestCase

from apps.pages.services.booking_total_price_service import BookingTotalPriceService


class BookingTotalPriceServiceTestCase(TestCase):
    def setUp(self):
        self.total_price_service = BookingTotalPriceService(
            price=30000, check_in_date="2024-11-01", check_out_date="2024-11-03"
        )

    def test_calculate_total_price(self):
        def test_calculate_total_price(self):
            # 2박이므로 총 가격은 30,000 * 2 = 60,000이어야 함
            expected_total_price = 30000 * 2
            calculated_total_price = self.total_price_service.calculate_price()

            # 예상한 가격과 실제 계산된 가격이 일치하는지 확인
            self.assertEqual(calculated_total_price, expected_total_price)

        def test_invalid_dates(self):
            # 체크인 날짜가 체크아웃 날짜보다 이후인 경우
            invalid_price_service = BookingTotalPriceService(
                price=30000, check_in_date="2024-11-03", check_out_date="2024-11-01"
            )

            # ValueError가 발생해야 함
            with self.assertRaises(ValueError):
                invalid_price_service.calculate_price()
