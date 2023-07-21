from email import message
from unicodedata import name
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm


def user_room_counting(user):
    rooms = Room.objects.filter(host=user.id)
    count = rooms.count()
    return count


def register_user(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()

            user.save()
            login(request, user)
            messages.success(request, 'Welcome ' + user.username + '!')
            return redirect('home')
        else:
            messages.error(request, 'Error during registration')

    context = {'form': form}
    return render(request, 'register_login.html', context)


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Update succesfully completed')
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'edit-user.html', context)


def login_user(request):
    page = 'login'

    if request.user.is_authenticated:
        messages.error(request, 'Invalid action!')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome ' + username + '!')
            return redirect('home')
        else:
            messages.error(request, 'User or password incorrect')
            return redirect('login')

    context = {'page': page}
    return render(request, 'register_login.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    recent_activity = user.message_set.all()
    topics = Topic.objects.all()
    room_count = user_room_counting(user)

    context = {
        'user': user,
        'rooms': rooms,
        'activity': recent_activity,
        'topics': topics,
        'room_count': room_count
    }

    return render(request, 'profile.html', context)


def home(request):
    q = request.GET.get('q')

    if q == None:
        rooms = Room.objects.all()
    else:
        rooms = Room.objects.filter(
            Q(topic__name=q) |
            Q(host__username=q) |
            Q(name__icontains=q)
        )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()

    if q != None:
        recent_activity = Message.objects.filter(
            Q(room__topic__name__icontains=q)
        )
    else:
        recent_activity = Message.objects.all()

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'activity': recent_activity
    }

    return render(request, 'home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    comments = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        Message.objects.create(
            room=room,
            user=request.user,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'comments': comments,
               'participants': participants}
    return render(request, 'room.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic').lower()
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'room-form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        messages.error(request, 'Invalid action!')
        return redirect('home')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'room': room}
    return render(request, 'room-form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        messages.error(request, 'Invalid action!')
        return redirect('home')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    context = {'obj': room}
    return render(request, 'delete.html', context)


@login_required(login_url='login')
def delete_message(request, pk):
    comment = Message.objects.get(id=pk)
    if request.user != comment.user:
        return HttpResponse('Invalid action!')

    if request.method == 'POST':
        comment.delete()
        return redirect('home')

    context = {'obj': comment}
    return render(request, 'delete.html', context)


def topics(request):
    q = request.GET.get('q')
    count = Topic.objects.all().count()
    if q != None:
        topics = Topic.objects.filter(name__icontains=q)
    else:
        topics = Topic.objects.all()

    context = {'topics': topics, 'count': count}
    return render(request, 'topics.html', context)


def recent_activity(request):
    recent_activity = Message.objects.all()
    context = {'recent_activity': recent_activity}
    return render(request, 'activity.html', context)
