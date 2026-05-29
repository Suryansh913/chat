from django.shortcuts import render
from chat.models import MyChats
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


@login_required
def index(request):

    frnd_name = request.GET.get('user', None)

    mychats_data = None

    if frnd_name:

        if User.objects.filter(username=frnd_name).exists():

            frnd_ = User.objects.get(username=frnd_name)

            if MyChats.objects.filter(
                me=request.user,
                frnd=frnd_
            ).exists():

                mychats_data = MyChats.objects.get(
                    me=request.user,
                    frnd=frnd_
                )

    frnd = User.objects.exclude(id=request.user.id)

    return render(request, 'index.html', {
        
        'chats': mychats_data,
        'frnds': frnd
    })