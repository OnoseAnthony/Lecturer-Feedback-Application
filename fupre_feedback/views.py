from django.shortcuts import render,redirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.http import HttpResponse

from reviews.models import Assessment


def HomePage(request):
    if request.user.is_authenticated:
        if request.user.is_instructor:
            return redirect('reviews:instructors:assessment_change_list')
        else:
            return redirect('reviews:students:assessment_list')

    news = Assessment.objects.all()
    fnames=""
    counters=0
    pcounts=0
    negcounts=0
    ncounts=0
    emailmessage = ""

    for assessment in news:
        counters +=1

        if (assessment.rating == -1):
            negcounts +=1
        elif (assessment.rating == 0):
            ncounts +=1
        elif (assessment.rating == 1):
            pcounts +=1
        else:
            print("It's possible the assessment hasn't be taken yet by any student yet")


    if (pcounts > negcounts and pcounts > ncounts):
        fnames =  "Excellent"

    elif (negcounts > pcounts and negcounts > ncounts):
        fnames = " Negative"

    else:
        fnames = "Neutral"


    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        from_email = request.POST.get('email')
        message = request.POST.get('message')
        try:
            send_mail(subject, message, from_email, [settings.EMAIL_HOST_USER], fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        emailmessage = "Received. we'd get back to you soon !!"


    return render(request, 'index.html', {'newsts': counters, 'poss': pcounts, 'negs': negcounts, 'neus': ncounts, 'fnames': fnames, 'emailmessages': emailmessage,})
