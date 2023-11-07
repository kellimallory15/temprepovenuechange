from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event, Package
# Import User Model From Django
from django.contrib.auth.models import User
from events.forms import PackageForm, EventForm, EventFormAdmin
from django.http import HttpResponse
import csv
from django.contrib import messages

# Import PDF Stuff
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# Import Pagination Stuff
from django.core.paginator import Paginator


# Show Event
def show_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    return render(request, 'events/show_booking.html', {
        "event": event
    })


# Show Events In A Package
def package_events(request, package_id):
    # Grab the package
    package = package.objects.get(id=package_id)
    # Grab the events from that package
    events = package.event_set.all()
    if events:
        return render(request, 'events/package_bookings.html', {
            "events": events
        })
    else:
        messages.success(request, ("That Package Has No Events At This Time..."))
        return redirect('admin_approval')


# Create Admin Event Approval Page
def admin_approval(request):
    # Get The Packages
    package_list = package.objects.all()
    # Get Counts
    event_count = Event.objects.all().count()
    package_count = package.objects.all().count()
    user_count = User.objects.all().count()

    event_list = Event.objects.all().order_by('-event_date')
    if request.user.is_superuser:
        if request.method == "POST":
            # Get list of checked box id's
            id_list = request.POST.getlist('boxes')

            # Uncheck all events
            event_list.update(approved=False)

            # Update the database
            for x in id_list:
                Event.objects.filter(pk=int(x)).update(approved=True)

            # Show Success Message and Redirect
            messages.success(request, ("Event List Approval Has Been Updated!"))
            return redirect('list-events')

        else:
            return render(request, 'events/admin_approval.html',
                          {"event_list": event_list,
                           "event_count": event_count,
                           "package_count": package_count,
                           "user_count": user_count,
                           "package_list": package_list})
    else:
        messages.success(request, ("You aren't authorized to view this page!"))
        return redirect('home')

    return render(request, 'events/admin_approval.html')


# Create My Events Page
def my_events(request):
    if request.user.is_authenticated:
        me = request.user.id
        events = Event.objects.filter(attendees=me)
        return render(request,
                      'events/my_bookings.html', {
                          "events": events
                      })

    else:
        messages.success(request, ("You Aren't Authorized To View This Page"))
        return redirect('home')


# Generate a PDF File Package List
def package_pdf(request):
    # Create Bytestream buffer
    buf = io.BytesIO()
    # Create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # Create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    # Add some lines of text
    # lines = [
    #	"This is line 1",
    #	"This is line 2",
    #	"This is line 3",
    # ]

    # Designate The Model
    packages = Package.objects.all()

    # Create blank list
    lines = []

    for package in packages:
        lines.append(package.name)
        lines.append(package.address)
        lines.append(package.zip_code)
        lines.append(package.phone)
        lines.append(package.web)
        lines.append(package.email_address)
        lines.append(" ")

    # Loop
    for line in lines:
        textob.textLine(line)

    # Finish Up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    # Return something
    return FileResponse(buf, as_attachment=True, filename='package.pdf')


# Generate CSV File Package List
def package_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=packages.csv'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate The Model
    package = Package.objects.all()

    # Add column headings to the csv file
    writer.writerow(['Package Name', 'Address', 'Zip Code', 'Phone', 'Web Address', 'Email'])

    # Loop Thu and output
    for package in packages:
        writer.writerow([package.name, package.address, package.zip_code, package.phone, package.web, package.email_address])

    return response


# Generate Text File Package List
def package_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=packages.txt'
    # Designate The Model
    packages = Package.objects.all()

    # Create blank list
    lines = []
    # Loop Thu and output
    for package in packages:
        lines.append(
            f'{package.name}\n{package.address}\n{package.zip_code}\n{package.phone}\n{package.web}\n{package.email_address}\n\n\n')

    # lines = ["This is line 1\n",
    # "This is line 2\n",
    # "This is line 3\n\n",
    # "John Elder Is Awesome!\n"]

    # Write To TextFile
    response.writelines(lines)
    return response


# Delete a Package
def delete_package(request, package_id):
    package = Package.objects.get(pk=package_id)
    package.delete()
    return redirect('list-package')


# Delete an Event
def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager:
        event.delete()
        messages.success(request, ("Event Deleted!!"))
        return redirect('list-events')
    else:
        messages.success(request, ("You Aren't Authorized To Delete This Event!"))
        return redirect('list-events')


def add_event(request):
    submitted = False
    if request.method == "POST":
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventForm(request.POST)
            if form.is_valid():
                # form.save()
                event = form.save(commit=False)
                event.manager = request.user  # logged in user
                event.save()
                return HttpResponseRedirect('/add_event?submitted=True')
    else:
        # Just Going To The Page, Not Submitting
        if request.user.is_superuser:
            form = EventFormAdmin
        else:
            form = EventForm

        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'events/add_booking.html', {'form': form, 'submitted': submitted})


def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        form = EventForm(request.POST or None, instance=event)

    if form.is_valid():
        form.save()
        return redirect('list-events')

    return render(request, 'events/update_booking.html',
                  {'event': event,
                   'form': form})


def update_package(request, package_id):
    package = Package.objects.get(pk=package_id)
    form = PackageForm(request.POST or None, request.FILES or None, instance=package)
    if form.is_valid():
        form.save()
        return redirect('list-packages')

    return render(request, 'events/update_package.html',
                  {'package': package,
                   'form': form})


def search_packages(request):
    if request.method == "POST":
        searched = request.POST['searched']
        package = Package.objects.filter(name__contains=searched)

        return render(request,
                      'events/search_packages.html',
                      {'searched': searched,
                       'packages': packages})
    else:
        return render(request,
                      'events/search_packages.html',
                      {})


def search_events(request):
    if request.method == "POST":
        searched = request.POST['searched']
        events = Event.objects.filter(description__contains=searched)

        return render(request,
                      'events/search_bookings.html',
                      {'searched': searched,
                       'events': events})
    else:
        return render(request,
                      'events/search_bookings.html',
                      {})


def show_package(request, package_id):
    package = Package.objects.get(pk=package_id)
    package_owner = User.objects.get(pk=package.owner)

    # Grab the events from that package
    events = package.event_set.all()

    return render(request, 'show_package.html',
                  {'package': package,
                   'package_owner': package_owner,
                   'events': events})


def list_packages(request):
    # package_list = package.objects.all().order_by('?')
    package_list = Package.objects.all()

    # Set up Pagination
    p = Paginator(Package.objects.all(), 3)
    page = request.GET.get('page')
    packages = p.get_page(page)
    nums = "a" * packages.paginator.num_pages
    return render(request, 'events/package.html',
                  {'package_list': package_list,
                   'packages': packages,
                   'nums': nums}
                  )


def add_package(request):
    submitted = False
    if request.method == "POST":
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save(commit=False)
            package.owner = request.user.id  # logged in user
            package.save()
            # form.save()
            return HttpResponseRedirect('/add_package?submitted=True')
    else:
        form = PackageForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'events/add_package.html', {'form': form, 'submitted': submitted})


def all_events(request):
    event_list = Event.objects.all().order_by('-event_date')
    return render(request, 'events/booking_list.html',
                  {'event_list': event_list})


def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = "John"
    month = month.capitalize()
    # Convert month from name to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    # create a calendar
    cal = HTMLCalendar().formatmonth(
        year,
        month_number)
    # Get current year
    now = datetime.now()
    current_year = now.year

    # Query the Events Model For Dates
    event_list = Event.objects.filter(
        event_date__year=year,
        event_date__month=month_number
    )

    # Get current time
    time = now.strftime('%I:%M %p')
    return render(request,
                  'events/home.html', {
                      "name": name,
                      "year": year,
                      "month": month,
                      "month_number": month_number,
                      "cal": cal,
                      "current_year": current_year,
                      "time": time,
                      "event_list": event_list,
                  })
