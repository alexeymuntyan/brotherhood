from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views import generic
from . import models
from .models import STATUS_CHOICES
from .forms import ExtendedSearch


def index(request):
    return render(request, template_name='bh/index.html', context={})


def people_list(request):
    p = models.Person.objects.order_by('last_name', 'first_name')
    return render(request, template_name='bh/people.html', context={
        'people': p
    })


def person(request, pk):
    p = get_object_or_404(models.Person, pk=pk)
    addresses = models.Address.objects.filter(
        lat__isnull=False, lng__isnull=False).all()
    return render(request, template_name='bh/person.html', context={
        'person': p, 'addresses': addresses
    })


def skill(request, pk):
    p = get_object_or_404(models.Skill, pk=pk)
    return render(request, template_name='bh/skill.html', context={
        'skill': p,
    })


def action(request, pk):
    a = get_object_or_404(models.Action, pk=pk)
    return render(request, template_name='bh/action.html', context={
        'action': a,
    })


def event(request, pk):
    e = get_object_or_404(models.Event, pk=pk)
    return render(request, template_name='bh/event.html', context={
        'event': e,
    })


def address(request, pk):
    p = get_object_or_404(models.Address, pk=pk)
    addresses = models.Address.objects.filter(
        lat__isnull=False, lng__isnull=False).all()
    return render(request, template_name='bh/address.html', context={
        'address': p, 'addresses': addresses
    })


class AddressList(generic.ListView):
    context_object_name = 'addresses'
    model = models.Address

    def get_queryset(self):
        return models.Address.objects.all()


class SkillList(generic.ListView):
    context_object_name = 'skills'
    model = models.Skill

    def get_queryset(self):
        return models.Skill.objects.order_by('name')


class ActionList(generic.ListView):
    context_object_name = 'actions'
    model = models.Action

    def get_queryset(self):
        return models.Action.objects.all()


class EventList(generic.ListView):
    context_object_name = 'events'
    model = models.Event

    def get_queryset(self):
        return models.Event.objects.all()


def status_list(request):
    return render(
        request, template_name='bh/status_list.html',
        context={'statuses': STATUS_CHOICES}
    )


def status(request, pk):
    p = models.Person.objects.filter(status=pk)
    s = STATUS_CHOICES[int(pk)]
    return render(
        request, template_name='bh/status_detail.html',
        context={'people': p, 'status': s}
    )


class PeriodList(generic.ListView):
    context_object_name = 'periods'
    model = models.Period

    def get_queryset(self):
        return models.Period.objects.order_by('dow', 'time_from', 'time_to')


def search(request):
    form = ExtendedSearch()
    p = None

    if request.method == 'POST':
        form = ExtendedSearch(request.POST)
        if form.is_valid():
            p = models.Person.objects

            baptized = int(form.cleaned_data.get('baptized'))
            if baptized <= 1:
                p = p.filter(baptized=bool(baptized))

            member = int(form.cleaned_data.get('member'))
            if member <= 1:
                p = p.filter(member=bool(member))

            married = int(form.cleaned_data.get('married'))
            if married <= 1:
                p = p.filter(married=bool(married))

            gender = form.cleaned_data.get('gender')
            if gender in ('m', 'f'):
                p = p.filter(gender=gender)

            status_int = int(form.cleaned_data.get('status'))
            if status_int < 1000:
                p = p.filter(status=status_int)

            show_gone_to_eternity = form.cleaned_data.get('gone_to_eternity')
            if not show_gone_to_eternity:
                p = p.filter(gone_to_eternity=False)

            show_gone_to_another_church = form.cleaned_data.get('gone_to_another_church')
            if not show_gone_to_another_church:
                p = p.filter(gone_to_another_church=False)

            show_gone = form.cleaned_data.get('gone')
            if not show_gone:
                p = p.filter(gone=False)

            # People, who makes action in all events
            event_presents = form.cleaned_data.get('event_presents')
            peoples = set()
            for ep in event_presents:
                pp = set()
                for e in models.Event.objects.filter(event_type=ep).all():
                    pp.update([p.id for p in e.people.all()])
                if peoples:
                    peoples = peoples.intersection(pp)
                else:
                    peoples = pp
            if len(event_presents):
                p = p.filter(pk__in=list(peoples))

            # People, who did not present in every event
            event_absents = form.cleaned_data.get('event_absents')
            peoples = set()
            for ep in event_absents:
                for e in models.Event.objects.filter(event_type=ep).all():
                    peoples.update([p.id for p in e.people.all()])
            if len(event_absents):
                p = p.exclude(pk__in=list(peoples))

            skills = form.cleaned_data.get('skills')
            if len(skills):
                p = p.filter(skills__in=skills)

            sort = int(form.cleaned_data.get('sort'))
            if sort == 1:
                p = p.order_by('-birthday')

    return render(
        request, template_name='bh/search.html',
        context={'form': form, 'people': p}
    )