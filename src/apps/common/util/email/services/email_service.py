from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.core.signing import TimestampSigner

from apps.common.constants.email_constants import VERIFY_EMAIL_URL


class EmailService:
    signer = TimestampSigner()

    def create_signed_email_token(self, email: str) -> str:
        signed_user_email = self.signer.sign(email)  # email: sign_data
        return signing.dumps(signed_user_email)  # 암호화

    def validate_email_token(self, token: str) -> str:
        decoded_user_email = signing.loads(token)
        return self.signer.unsign(decoded_user_email, max_age=60 * 10)

    @staticmethod
    def get_verification_email_content(token: str) -> tuple[str, str]:
        url = VERIFY_EMAIL_URL + token
        subject = "이메일 인증을 완료해주세요"
        message = f"다음 링크를 클릭해 주세요. {url}"

        return subject, message

    @staticmethod
    def send_email(subject: str, message: str, to_email: str) -> None:
        email = to_email if isinstance(to_email, list) else [to_email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, email)
