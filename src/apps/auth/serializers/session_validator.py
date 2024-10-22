# from rest_framework.exceptions import ValidationError
#
#
# class SessionValidator:
#     @staticmethod
#     def validate_reset_email_in_session(session: dict) -> str:
#         email = session.get("reset_email")
#         if not email:
#             raise ValidationError("No email found in session.")
#         return email
#
#     @staticmethod
#     def validate_user_data_in_session(session: dict) -> None:
#         user_data = session.get("user_data")
#         if not user_data:
#             raise ValidationError("User data not found in session.")
#
#     @staticmethod
#     def validate_otp_verified_in_session(session: dict) -> None:
#         otp_verified = session.get("otp_verified")
#         if not otp_verified:
#             raise ValidationError("OTP verification required.")
