VERIFICATION_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("in_review", "In Review"),
    ("additional_info_required", "Additional Information Required"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("suspended", "Suspended"),
]

BOOKING_STATUS_CHOICES = [
    ("pending", "Pending"),  # 예약이 생성되었지만 아직 확정되지 않은 상태입니다. 결제나 승인이 필요할 수 있습니다.
    ("confirmed", "Confirmed"),  # 예약이 확정된 상태입니다. 모든 필요한 조건이 충족되었고, 예약이 성사되었습니다.
    ("paid", "Paid"),  # 예약 금액이 전액 결제된 상태입니다.
    ("partially_paid", "Partially Paid"),  # 예약 금액 중 일부만 결제된 상태. 나머지 금액의 결제가 필요할 수 있습니다.
    ("check_in", "Checked In"),  # 손님이 숙소에 체크인한 상태입니다.
    ("check_out", "Checked Out"),  # 손님이 숙소에서 체크아웃한 상태입니다. 이용이 종료되었습니다.
    ("cancelled_by_guest", "Cancelled by Guest"),  # 손님이 예약을 취소한 상태입니다.
    ("cancelled_by_host", "Cancelled by Host"),  # 호스트가 예약을 취소한 상태입니다.
    ("no_show", "No Show"),  # 손님이 예약된 날짜에 나타나지 않은 상태입니다. 체크인하지 않은 경우를 의미합니다.
    ("refunded", "Refunded"),  # 예약이 취소되거나 기타 이유로 환불이 완료된 상태입니다.
    (
        "completed",
        "Completed",
    ),  # 이용이 완료된 상태입니다. 체크인, 체크아웃이 모두 끝난 상태로, 예약 과정이 정상적으로 마무리되었습니다.
]

RATING_CHOICES = [
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
]

GENDER_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
]

USER_TYPE_CHOICES = [
    ("guest", "Guest"),
    ("host", "Host"),
    ("admin", "Administrator"),
]

SOCIAL_LOGIN_CHOICES = [
    ("google", "Google"),
    ("facebook", "Facebook"),
    ("twitter", "Twitter"),
    ("none", "None"),
]

# Room type choices
ROOM_TYPE_CHOICES = [
    ("deluxe", "Deluxe"),
    ("suite", "Suite"),
    ("standard", "Standard"),
    ("premium", "Premium"),
    ("family", "Family"),
    ("economy", "Economy"),
]

# Accommodation type choices
ACCOMMODATION_TYPE_CHOICES = [
    ("hotel", "Hotel"),
    ("resort", "Resort"),
    ("pension", "Pension"),
    ("guesthouse", "Guesthouse"),
    ("hostel", "Hostel"),
    ("motel", "Motel"),
    ("campsite", "Campsite"),
]

AMENITY_CATEGORIES_CHOICES = [
    ("basic", "Basic"),
    ("entertainment", "Entertainment"),
    ("kitchen", "Kitchen"),
    ("safety", "Safety"),
    ("outdoor", "Outdoor"),
    ("wellness", "Wellness"),
    ("others", "Others"),
]
AMENITY_CHOICES = [
    ("free_wifi", "Free Wi-Fi"),
    ("heating", "Heating"),
    ("air_conditioning", "Air conditioning"),
    ("tv", "TV"),
    ("hot_water", "Hot water"),
    ("private_entrance", "Private entrance"),
    ("cable_tv", "Cable TV"),
    ("streaming_services", "Streaming services (e.g., Netflix)"),
    ("gaming_console", "Gaming console"),
    ("sound_system", "Sound system"),
    ("refrigerator", "Refrigerator"),
    ("stove", "Stove"),
    ("microwave", "Microwave"),
    ("coffee_maker", "Coffee maker"),
    ("dishwasher", "Dishwasher"),
    ("cooking_basics", "Cooking basics"),
    ("fire_extinguisher", "Fire extinguisher"),
    ("smoke_detector", "Smoke detector"),
    ("first_aid_kit", "First aid kit"),
    ("security_cameras", "Security cameras"),
    ("pool", "Pool"),
    ("bbq_grill", "BBQ grill"),
    ("outdoor_dining_area", "Outdoor dining area"),
    ("garden", "Garden"),
    ("hot_tub", "Hot tub"),
    ("sauna", "Sauna"),
    ("gym_equipment", "Gym equipment"),
    ("massage_chair", "Massage chair"),
    ("free_parking", "Free parking"),
    ("luggage_storage", "Luggage storage"),
    ("pet_friendly", "Pet-friendly"),
    ("breakfast_included", "Breakfast included"),
]

# Option 카테고리
OPTION_CATEGORIES_CHOICES = [
    ("service", "Service"),
    ("extras", "Extras"),
    ("room_features", "Room Features"),
]

# Option 선택 항목
OPTION_CHOICES = [
    # Service 관련 옵션
    ("daily_housekeeping", "Daily housekeeping"),
    ("room_service", "Room service"),
    ("laundry_service", "Laundry service"),
    ("airport_shuttle", "Airport shuttle"),
    ("breakfast_in_room", "Breakfast in room"),
    ("wake_up_call", "Wake-up call"),
    ("concierge_service", "Concierge service"),
    # Extras 관련 옵션
    ("extra_bed", "Extra bed"),
    ("late_check_out", "Late check-out"),
    ("early_check_in", "Early check-in"),
    ("parking_spot", "Parking spot"),
    ("baby_crib", "Baby crib"),
    ("mini_bar", "Mini bar"),
    ("soundproof_windows", "Soundproof windows"),
    ("balcony", "Balcony"),
    ("coffee_machine", "Coffee machine"),
    # Room Features 관련 옵션
    ("blackout_curtains", "Blackout curtains"),
    ("soundproof_windows", "Soundproof windows"),
    ("private_balcony", "Private balcony"),
    ("in_room_safe", "In-room safe"),
    ("smart_tv", "Smart TV"),
    ("bluetooth_speakers", "Bluetooth speakers"),
    ("air_purifier", "Air purifier"),
    ("heater", "Heater"),
]

# Amenity 카테고리와 선택 항목 묶음
AMENITY_CHOICES_BY_CATEGORY = {
    "basic": [
        ("free_wifi", "Free Wi-Fi"),
        ("heating", "Heating"),
        ("air_conditioning", "Air conditioning"),
        ("tv", "TV"),
        ("hot_water", "Hot water"),
        ("private_entrance", "Private entrance"),
    ],
    "entertainment": [
        ("cable_tv", "Cable TV"),
        ("streaming_services", "Streaming services (e.g., Netflix)"),
        ("gaming_console", "Gaming console"),
        ("sound_system", "Sound system"),
    ],
    "kitchen": [
        ("refrigerator", "Refrigerator"),
        ("stove", "Stove"),
        ("microwave", "Microwave"),
        ("coffee_maker", "Coffee maker"),
        ("dishwasher", "Dishwasher"),
        ("cooking_basics", "Cooking basics"),
    ],
    "safety": [
        ("fire_extinguisher", "Fire extinguisher"),
        ("smoke_detector", "Smoke detector"),
        ("first_aid_kit", "First aid kit"),
        ("security_cameras", "Security cameras"),
    ],
    "outdoor": [
        ("pool", "Pool"),
        ("bbq_grill", "BBQ grill"),
        ("outdoor_dining_area", "Outdoor dining area"),
        ("garden", "Garden"),
    ],
    "wellness": [
        ("hot_tub", "Hot tub"),
        ("sauna", "Sauna"),
        ("gym_equipment", "Gym equipment"),
        ("massage_chair", "Massage chair"),
    ],
    "others": [
        ("free_parking", "Free parking"),
        ("luggage_storage", "Luggage storage"),
        ("pet_friendly", "Pet-friendly"),
        ("breakfast_included", "Breakfast included"),
    ],
}

# Option 카테고리와 선택 항목 묶음
OPTION_CHOICES_BY_CATEGORY = {
    "service": [
        ("daily_housekeeping", "Daily housekeeping"),
        ("room_service", "Room service"),
        ("laundry_service", "Laundry service"),
        ("airport_shuttle", "Airport shuttle"),
        ("breakfast_in_room", "Breakfast in room"),
        ("wake_up_call", "Wake-up call"),
        ("concierge_service", "Concierge service"),
    ],
    "extras": [
        ("extra_bed", "Extra bed"),
        ("late_check_out", "Late check-out"),
        ("early_check_in", "Early check-in"),
        ("parking_spot", "Parking spot"),
        ("baby_crib", "Baby crib"),
        ("mini_bar", "Mini bar"),
        ("soundproof_windows", "Soundproof windows"),
        ("balcony", "Balcony"),
        ("coffee_machine", "Coffee machine"),
    ],
    "room_features": [
        ("blackout_curtains", "Blackout curtains"),
        ("soundproof_windows", "Soundproof windows"),
        ("private_balcony", "Private balcony"),
        ("in_room_safe", "In-room safe"),
        ("smart_tv", "Smart TV"),
        ("bluetooth_speakers", "Bluetooth speakers"),
        ("air_purifier", "Air purifier"),
        ("heater", "Heater"),
    ],
}

STATE_CHOICES = [
    ("서울특별시", "서울특별시"),
    ("부산광역시", "부산광역시"),
    ("대구광역시", "대구광역시"),
    ("인천광역시", "인천광역시"),
    ("광주광역시", "광주광역시"),
    ("대전광역시", "대전광역시"),
    ("울산광역시", "울산광역시"),
    ("세종특별자치시", "세종특별자치시"),
    ("경기도", "경기도"),
    ("강원도", "강원도"),
    ("충청북도", "충청북도"),
    ("충청남도", "충청남도"),
    ("전라북도", "전라북도"),
    ("전라남도", "전라남도"),
    ("경상북도", "경상북도"),
    ("경상남도", "경상남도"),
    ("제주특별자치도", "제주특별자치도"),
]

STATE_COORDINATES = {
    "서울특별시": (126.9780, 37.5665),
    "부산광역시": (129.0756, 35.1796),
    "대구광역시": (128.6014, 35.8714),
    "인천광역시": (126.7052, 37.4563),
    "광주광역시": (126.8526, 35.1595),
    "대전광역시": (127.3845, 36.3504),
    "울산광역시": (129.3114, 35.5384),
    "세종특별자치시": (127.2817, 36.4871),
    "경기도": (127.5183, 37.4138),
    "강원도": (128.1555, 37.8228),
    "충청북도": (127.4914, 36.6357),
    "충청남도": (126.8000, 36.5184),
    "전라북도": (127.1530, 35.7175),
    "전라남도": (126.9910, 34.8679),
    "경상북도": (128.8889, 36.4919),
    "경상남도": (128.2132, 35.4606),
    "제주특별자치도": (126.5312, 33.4996),
}
