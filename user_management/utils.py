from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import traceback


def send_otp_email(user_email, otp, username, purpose="verify"):
    """
    Send HTML OTP email for verification or password reset.

    purpose: "verify" | "reset"
    """
    try:
        # Email subject and template selection
        if purpose == "verify":
            subject = "Verify your email - CMS Account"
            template_name = "emails/verify_email.html"
            intro_text = "Thank you for registering with CMS!"
            action_text = "Please use the following OTP to verify your email address:"
        else:
            subject = "Reset your password - CMS Account"
            template_name = "emails/reset_password.html"
            intro_text = "We received a request to reset your CMS account password."
            action_text = "Use the following OTP to reset your password:"

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@cms.com")
        recipient_list = [user_email]

        context = {
            "username": username,
            "otp": otp,
            "purpose": purpose,
            "intro_text": intro_text,
            "action_text": action_text,
        }

        # ✅ Render HTML version
        html_content = render_to_string(template_name, context)

        # ✅ Plain text fallback
        text_content = f"""
        Hi {username},

        {intro_text}
        {action_text}

        OTP: {otp}

        This code will expire in 10 minutes.
        If you did not request this, please ignore this email.
        """

        # ✅ Build and send
        msg = EmailMultiAlternatives(subject, text_content.strip(), from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        print(f"[✅] {purpose.capitalize()} email sent successfully to {user_email}")

    except Exception as e:
        print(f"[❌] Failed to send {purpose} email to {user_email}: {str(e)}")
        traceback.print_exc()
