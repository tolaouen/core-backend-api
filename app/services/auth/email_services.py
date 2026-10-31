import secrets
from datetime import datetime, timezone

from app.constants.constant import OTPPurposeEnum
from app.core.config import settings


class EmailService:
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        return "".join(str(secrets.randbelow(10)) for _ in range(length))

    @staticmethod
    async def send_otp_email(
        email: str, otp: str, purpose: str = OTPPurposeEnum.SIGNUP
    ) -> bool:
        print("\n" + "=" * 60)
        print("📧 EMAIL SENT (DEVELOPMENT MODE)")
        print("=" * 60)
        print(f"To: {email}")
        print(f"Subject: Your {purpose.title()} OTP Code")
        print("Body:")
        print(f"  Your OTP code is: {otp}")
        print(f"  This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.")
        print("  Do not share this code with anyone.")
        print("=" * 60 + "\n")

        # TODO: Replace with real email service in production
        # Example with SendGrid:
        # import sendgrid
        # sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        # message = Mail(...)
        # sg.send(message)

        return True

    @staticmethod
    async def send_welcome_email(email: str, username: str) -> bool:
        print(f"\n📧 Welcome email sent to {email} ({username})\n")
        return True

    @staticmethod
    async def send_password_reset_confirmation(email: str, username: str) -> bool:
        """Send confirmation email after password reset"""
        print("\n" + "=" * 60)
        print("📧 EMAIL SENT (DEVELOPMENT MODE)")
        print("=" * 60)
        print(f"To: {email}")
        print("Subject: Password Reset Successful")
        print("Body:")
        print(f"  Hi {username},")
        print("  Your password has been successfully reset.")
        print("  If you did not make this change, please contact support immediately.")
        print("  You have been logged out from all devices for security.")
        print("=" * 60 + "\n")

        # TODO: Replace with real email service in production
        return True

    @staticmethod
    async def send_password_changed_email(email: str, username: str) -> bool:
        print("\n" + "=" * 60)
        print("📧 EMAIL SENT (DEVELOPMENT MODE)")
        print("=" * 60)
        print(f"To: {email}")
        print("Subject: Password Changed Successfully")
        print("Body:")
        print(f"  Hi {username},")
        print("")
        print("  Your password has been changed successfully.")
        print("")
        print(
            f"  Date: {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}"
        )
        print("")
        print("  For security reasons, you have been logged out from all devices.")
        print("  Please login again with your new password.")
        print("")
        print("  If you did not make this change, please contact support immediately.")
        print("=" * 60 + "\n")

        return True
