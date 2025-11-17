from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail

User = get_user_model()


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
 
    if created:
        token = default_token_generator.make_token(instance)

        path = reverse('activate_user', args=[instance.id, token])
        activation_url = f"{settings.FRONTEND_URL}{path}"

        subject = "Activate Your Account"
        message = (
            f"Hi {instance.username},\n\n"
            "Please activate your account using the link below:\n"
            f"{activation_url}\n\n"
            "Thank you!"
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=False
            )
        except Exception as e:
            print(f"Failed to send email to {instance.email}: {e}")


@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    
    if created:
        group, _ = Group.objects.get_or_create(name="User")
        instance.groups.add(group)
