from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings


def contact(request):
    """ Returns the home page """
    if request.method == 'POST':
        name = request.POST.get('user_name')
        email = request.POST.get('user_email')
        phone = request.POST.get('user_phone')
        message = request.POST.get('user_text')
        subject = f"Email from {name} @ {email}"
        content = f"Name: {name}\nEmail: {email}\nPhone:" \
            f"{phone}\nMessage:\n{message}"
        send_mail(
            subject, content, settings.EMAIL_HOST_USER,
            ["johnmcdaid@outlook.com"], fail_silently=False)
        return render(request, 'contact/contact_success.html')

    return render(request, 'contact/contact.html')
