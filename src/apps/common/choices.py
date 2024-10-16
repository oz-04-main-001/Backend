VERIFICATION_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("in_review", "In Review"),
    ("additional_info_required", "Additional Information Required"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("suspended", "Suspended"),
]

BOOKING_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("confirmed", "Confirmed"),
    ("paid", "Paid"),
    ("partially_paid", "Partially Paid"),
    ("check_in", "Checked In"),
    ("check_out", "Checked Out"),
    ("cancelled_by_guest", "Cancelled by Guest"),
    ("cancelled_by_host", "Cancelled by Host"),
    ("no_show", "No Show"),
    ("refunded", "Refunded"),
    ("completed", "Completed"),
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
