from django.shortcuts import render, redirect
from .models import Note, Label
from .forms import NotesForm, LabelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
import logging
from django.contrib.auth.decorators import login_required, permission_required

logger = logging.getLogger(__name__)


@login_required
def index(request, label_id=None):
    if label_id is not None:
        current_label = Label.objects.get(id=label_id)
        if current_label:
            tmp_notes = Note.objects.filter(owner=request.user).filter(label_id=current_label.id)
        else:
            tmp_notes = Note.objects.filter(owner=request.user)
    else:
        tmp_notes = Note.objects.filter(owner=request.user)

    labels = Label.objects.filter(owner=request.user)
    pinned = [x for x in tmp_notes if x.pinned]
    notes = set(tmp_notes) - set(pinned)
    return render(request, 'notes/index.html', {'notes': notes, 'labels': labels, 'pinned': pinned})


@login_required
def notes_edit(request, id):
    if request.method == 'POST':
        form = NotesForm(request.POST)

        if form.is_valid():
            note = Note.objects.filter(owner=request.user).get(id=id)
            note.title = form.cleaned_data['title']
            note.pinned = form.cleaned_data['pinned']
            note.content = form.cleaned_data['content']
            note.label = form.cleaned_data['label']
            note.save()
            messages.success(request, 'Note edited successfully')
            return redirect('notes:index')
        else:
            return render(request, 'notes/edit.html', {'form': form, 'id': id})
    else:
        note = Note.objects.filter(owner=request.user).get(id=id)
        form = NotesForm(instance=note)
        form.fields['label'].queryset = Label.objects.filter(owner_id=request.user.id)
        return render(request, 'notes/edit.html', {'form': form, 'id': id})


@login_required
def notes_delete(request, id):
    if request.method == 'POST':
        note = Note.objects.filter(owner=request.user).get(id=id)
        note.delete()
        messages.success(request, 'Note deleted successfully')
    return redirect('notes:index')


@login_required
def notes_create(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            note = Note()
            note.title = form.cleaned_data['title']
            note.pinned = form.cleaned_data['pinned']
            note.content = form.cleaned_data['content']
            note.label = form.cleaned_data['label']
            note.owner = request.user
            note.save()
            messages.success(request, 'Note created successfully')
            return redirect('notes:index')
        else:
            return render(request, 'notes/create.html', {'form': form })
    else:
        form = NotesForm()
        form.fields['label'].queryset = Label.objects.filter(owner_id=request.user.id)
        return render(request, 'notes/create.html', {'form': form})


@login_required
def labels_create(request):
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            label = Label()
            label.title = form.cleaned_data['title']
            label.color = form.cleaned_data['color']
            label.owner = request.user
            label.save()
            messages.success(request, 'Label created successfully')
            return redirect('notes:index')
        else:
            return render(request, 'labels/create.html', {'form': form})
    else:
        form = LabelForm()
        return render(request, 'labels/create.html', {'form': form})


@login_required
def labels_edit(request, id):
    if request.method == 'POST':
        form = LabelForm(request.POST)

        if form.is_valid():
            label = Label.objects.filter(owner=request.user).get(id=id)
            label.title = form.cleaned_data['title']
            label.color = form.cleaned_data['color']
            label.save()
            messages.success(request, 'Label edited successfully')
            return redirect('notes:index')
        else:
            return render(request, 'labels/edit.html', {'form': form, 'id': id})
    else:
        label = Label.objects.filter(owner=request.user).get(id=id)
        form = LabelForm(instance=label)
        return render(request, 'labels/edit.html', {'form': form, 'id': id})


@login_required
def labels_delete(request, id):
    if request.method == 'POST':
        label = Label.objects.filter(owner=request.user).get(id=id)
        label.delete()
        messages.success(request, 'Label deleted successfully')
    return redirect('notes:index')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            raw_password = form.cleaned_data['password1']
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('notes:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
