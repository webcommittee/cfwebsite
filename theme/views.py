import json
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from models import CompanyProfile, StudentProfile
from models import RegistrationPage
from models import ArmoryTableData
from models import CompanyRep
from models import PayPalInfo
from models import SponsorshipPackage
from models import SponsorshipItem
from forms import UserForm, StudentProfileForm, CompanyProfileForm, CompanySearchForm, EditCompanyProfileForm, StudentSearchForm, RepForm, BaseRepFormSet
from django.forms.formsets import formset_factory
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from paypal.standard.forms import PayPalPaymentsForm
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from email.MIMEImage import MIMEImage

NGROK =  "http://rpicareerfair.org"

from django.contrib.auth.decorators import user_passes_test
def has_submitted_payment(user):
    try:
        company = user.companyprofile
    except:
        return False or user.is_staff
    return company.has_submitted_payment or user.is_staff

def has_not_submitted_payment(user):
    try:
	company = user.companyprofile
    except:
	return True
    return not company.has_submitted_payment

# A view hooked up to the page
def send_custom_email(page_type, user):
    if page_type.send_email:
        subject = page_type.email_subject
        message = page_type.email_message
	if page_type.email_copies:
            email_to = page_type.email_copies.split(",")
            email_to += [user.email]
        else:
            email_to = [user.email]
	d = Context({"email_message":message})
	send_invoice(page_type, user)
	plaintext = get_template('pages/custom_reg_email.txt')
	htmly = get_template('pages/custom_reg_email.html')
	text_content = plaintext.render(d)
	html_content = htmly.render(d)
	email = EmailMultiAlternatives(subject, text_content, 'Career Fair Staff', email_to)
	email.attach_alternative(html_content, "text/html")
	try:
	    attachment = open(page_type.attachment.url[1:],'r')
        except:
	    attachment = None
	if attachment:
		email.attach("nsbe_shpe_cf_confirmation_packet.pdf", attachment.read(), 'application/pdf') 
	email.send(fail_silently=False)

def send_invoice(page_type, user):
    if page_type.send_email:
	subject= page_type.email_subject
	try:
	    attachment = open(page_type.attachment.url[1:],'r')
	except:
	    attachment=None
	email_to = [user.email]
        #Ruben had hardcoded the two lines below this one. The lines from the send_custom_email function were used for this function after realizing that the hardcoded lines broke sending emails
	#plaintext = get_template("/opt/myenv/careerfair"+page_type.invoice_template_text.url)
	#htmly = get_template("/opt/myenv/careerfair"+page_type.invoice_template_html.url)
        plaintext = get_template('pages/invoice.txt')
	htmly = get_template('pages/invoice.html')
	try:
	    sponsorship = SponsorshipPackage.objects.get(title=user.companyprofile.sponsor)
	except:
	    sponsorship = None
	d = Context({'sponsorship':sponsorship, 'paypal_info': PayPalInfo.objects.all()[0], 'company':user.companyprofile})
	text_content = plaintext.render(d)
	html_content = htmly.render(d)
	email = EmailMultiAlternatives(subject, text_content, 'Career Fair Staff', email_to)
	email.attach_alternative(html_content, "text/html")
	email.mixed_subtype = 'related'
	email.send()

def update_rep_data(company):
    company.friday_representatives.clear()
    company.saturday_representatives.clear()
    for rep in company.reps.all():
	if "Friday" in rep.days_attending:
	    company.friday_representatives.add(rep)
        if "Saturday" in rep.days_attending:
	    company.saturday_representatives.add(rep)
    company.save()

# Calculates a company's registration price based off the
# PayPalInfo object the administrative user provided and
	# the company's signup info.
def get_bill(company):
    # Retrie ve the admin spcified prices
    paypal_info = PayPalInfo.objects.all()[0]
    total_bill = 0
    if company.user.is_staff:
	return paypal_info.email, paypal_info.item_name, 1
    # Calculate the base price based off the days attending
    if "Friday" in company.days_attending and "Saturday" in company.days_attending:
	total_bill += paypal_info.weekend_price
    elif "Friday" in company.days_attending:
	total_bill += paypal_info.friday_price
    elif "Saturday" in company.days_attending:
        total_bill += paypal_info.saturday_price


    # Add additional rep fee for each rep beyond the first two
    sponsorship = company.sponsor
    count = 2 * len(company.days_attending)
    num_reps_attending = len(company.friday_representatives.all())+len(company.saturday_representatives.all())
    total_bill += ((num_reps_attending - count) * paypal_info.price_per_rep) if num_reps_attending > count else 0

    count = 0 - len(company.days_attending)
    num_tables = company.friday_number_of_tables + company.saturday_number_of_tables
    total_bill += (num_tables+count) * paypal_info.price_per_table if num_tables > count else  0
   
    if sponsorship:
	sponsorship = SponsorshipPackage.objects.get(title=company.sponsor)
    	total_bill -= paypal_info.price_per_rep*sponsorship.num_free_reps
	total_bill -= paypal_info.price_per_table*sponsorship.num_free_tables
	total_bill += sponsorship.price
	total_bill -= sponsorship.discount

    for item in company.sponsorshipitem.all():
	total_bill += item.price

    if company.is_non_profit:
	total_bill *= 0.85
    return paypal_info.email, paypal_info.item_name, total_bill


# A complicated and student function that parses the CompanyProfileForm
# and saves all the information into a user and a companyprofile.
# It parses the post request for all the form information, as well as
# the logo, and representative names.
def company_register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False


    RepFormSet = formset_factory(RepForm, formset=BaseRepFormSet)

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
	# TODO:
	#return HttpResponse("Registration has closed!")
	
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
	temp_email = request.POST['username']
        if len(request.POST['username']) > 30:
	    request.POST['username'] = request.POST['username'][:30]
	user_form = UserForm(request.POST, request.FILES)
        profile_form = CompanyProfileForm(request.POST, request.FILES)
        rep_formset = RepFormSet(request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid() and rep_formset.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            user.email=temp_email

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model. "
            if 'logo' in request.FILES:
                profile.logo = request.FILES['logo']

            else:
                profile.logo = 'uploads/default_icons/Company_icon.png'

            profile.save()


	    if 'sponsorshipitem' in  request.POST:
	   	for item in request.POST.getlist('sponsorshipitem'):
		    profile.sponsorshipitem.add(SponsorshipItem.objects.get(name=item))
            # Now we save the CompanyProfile model instance.
            

            # Create a bunch of representative objects
            new_reps = []

            for rep_form in rep_formset:
                rep = rep_form.cleaned_data.get('rep')
                is_alumni = rep_form.cleaned_data.get('is_alumni')
		days_attending = rep_form.cleaned_data.get('days_attending')
                if rep:
                    new_rep = CompanyRep(user=user, rep=rep, is_alumni=is_alumni, company=profile.company, days_attending=days_attending)
                    new_reps.append(new_rep)

            CompanyRep.objects.bulk_create(new_reps)

            # Associate the new reps with the CompanyProfile 
            for rep in CompanyRep.objects.filter(user=user):
                profile.reps.add(rep)
            for rep in CompanyRep.objects.filter(user=user, is_alumni=True):
                profile.reps_alumni.add(rep)
           
	    update_rep_data(profile) 
            profile.number_of_representatives = len(new_reps)
	    profile.number_of_tables = profile.friday_number_of_tables + profile.saturday_number_of_tables
            email, item, bill = get_bill(profile)
            profile.total_bill = bill 
            new_user = profile.save()
            new_user = authenticate(username=user_form.cleaned_data['username'],
                                    password=user_form.cleaned_data['password'],)



            # Update our variable to tell the template registration was successful.
            registered = True

            # send email
            page_type = RegistrationPage.objects.get(title="Company Registration").registrationpage
            send_custom_email(page_type, user)


            # Log in the user upon creation of account
            login(request, new_user)

            #redirect them to their dashboard
            return HttpResponseRedirect("/dashboard/")

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = CompanyProfileForm()
        rep_formset = RepFormSet()

    context["form"] = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered, 'rep_formset':rep_formset}

    # Render the template depending on the context.
    return render_to_response(
            'pages/company-registration.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered, 'rep_formset':rep_formset},
            context)


# Student registration.  Very similar to the company registration view
# a tiny bit simpler though.
def student_register(request):
    context = RequestContext(request)
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = StudentProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # set the email to the username
            user.email=user.username
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.first_name = user.first_name
            profile.last_name = user.last_name
            if 'resume' in request.FILES:
                profile.resume = request.FILES['resume']

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            else:
                profile.picture = 'defaults/Student_icon.png'

            registered = True
            new_user = profile.save()
            new_user = authenticate(username=user_form.cleaned_data['username'],
                                    password=user_form.cleaned_data['password'])

            page_type = RegistrationPage.objects.get(title="Student Registration").registrationpage
            #send_custom_email(page_type, user) Currently broken. May try to fix later

            login(request, new_user)

            return HttpResponseRedirect("/dashboard/")

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = StudentProfileForm()

    context["form"] = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}

    return render_to_response(
            'pages/student-registration.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']
	if len(username) > 30:
	    username = username[:30]
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            # lazy: make it return nothing so django throws an error so 
            return  

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('login.html', {}, context)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')

@login_required
def prepayment_page(request):
    if request.method == 'POST':
        pass
    return render_to_response('pages/prepaymentscreen.html',{}, RequestContext(request))

@login_required
def payment_page(request):
    if request.method == 'post':
        pass
    return render_to_response('pages/payment_page.html' , {} , RequestContext(request))

@login_required
@user_passes_test(has_not_submitted_payment, login_url="/dashboard/")
def edit_profile(request):
    user = request.user
    RepFormSet = formset_factory(RepForm, formset=BaseRepFormSet)
    is_company = True

    try:
        user.studentprofile
        is_company = False
    except AttributeError:
        pass

    if is_company: 
        form = EditCompanyProfileForm(request.POST or None, initial={'company':user.companyprofile.company, 
                                                                'company_website':user.companyprofile.company_website,
                                                                'logo':user.companyprofile.logo,
                                                                'days_attending':user.companyprofile.days_attending,
                                                                'majors_wanted':user.companyprofile.majors_wanted,
                                                                'grade_level_wanted':user.companyprofile.grade_level_wanted,
                                                                'company_bio':user.companyprofile.company_bio,
                                                                'sponsor':user.companyprofile.sponsor,
								'sponsorshipitem':[s.name for s in user.companyprofile.sponsorshipitem.all()],
                                                                'friday_number_of_tables':user.companyprofile.friday_number_of_tables,
                                                                'saturday_number_of_tables':user.companyprofile.saturday_number_of_tables,
                                                                'interview_rooms_friday': user.companyprofile.interview_rooms_friday,
                                                                'interview_friday_from': user.companyprofile.interview_friday_from,
                                                                'interview_friday_to':user.companyprofile.interview_friday_to,
                                                                'interview_rooms_saturday':user.companyprofile.interview_rooms_saturday,
                                                                'interview_saturday_from': user.companyprofile.interview_saturday_from,
                                                                'interview_saturday_to:':user.companyprofile.interview_saturday_to,
                                                                })
        rep_links = CompanyRep.objects.filter(user=user).order_by('rep')
        rep_data = [{'rep': l.rep, 'is_alumni': l.is_alumni, 'days_attending':l.days_attending}
                    for l in rep_links]
        rep_formset = RepFormSet(initial=rep_data)
        
    else:
        # not a company, display the student edit profile form
        form = StudentProfileForm(request.POST or None, initial={'first_name':user.studentprofile.first_name,
                                                                 'last_name':user.studentprofile.last_name,
                                                                 'phone_number':user.studentprofile.phone_number,
                                                                 'picture':user.studentprofile.picture,
                                                                 'hometown':user.studentprofile.hometown,
                                                                 'resume':user.studentprofile.resume,
                                                                 'open_to_relocation':user.studentprofile.open_to_relocation,
                                                                 'major':user.studentprofile.major,
                                                                 'minor':user.studentprofile.minor,
                                                                 'grade_level':user.studentprofile.grade_level,
                                                                 'website':user.studentprofile.website,
                                                                 'GPA':user.studentprofile.GPA,
                                                             }, instance=user.studentprofile)
        rep_formset=None

    # If we a posting, start saving the new information
    if request.method == 'POST':
        if is_company:
            # RepFormSet is the thing that allows us to associate many reps with one company
            form = EditCompanyProfileForm(request.POST, instance=user.companyprofile)
            rep_formset = RepFormSet(request.POST)
            if form.is_valid() and rep_formset.is_valid():
                profile = form.save(commit=False)
                profile.user = user
                
                #If they chose to delete their logo, reset the url to be
                if 'logo-clear' in request.POST:
                    profile.logo = 'uploads/default_icons/Company_icon.png'
                if 'logo' in request.FILES:
                    profile.logo = request.FILES['logo']
                profile.save()
		profile.number_of_tables = profile.friday_number_of_tables + profile.saturday_number_of_tables

                # Representative parsing and saving
                new_reps = []
                for rep_form in rep_formset:
                    rep = rep_form.cleaned_data.get('rep')
                    is_alumni = rep_form.cleaned_data.get('is_alumni')
		    days_attending = rep_form.cleaned_data.get('days_attending')
                    if rep:
                        new_rep = CompanyRep(user=user, rep=rep, is_alumni=is_alumni, company=user.companyprofile.company, days_attending=days_attending)
                        new_reps.append(new_rep)

                CompanyRep.objects.filter(user=user).delete()
                CompanyRep.objects.bulk_create(new_reps)
                for rep in CompanyRep.objects.filter(user=user):
                    profile.reps.add(rep)
                for rep in CompanyRep.objects.filter(user=user, is_alumni=True):
                    profile.reps_alumni.add(rep)
		update_rep_data(profile)
		profile.sponsorshipitem.clear()
		if 'sponsorshipitem' in request.POST:
		    for item in request.POST.getlist('sponsorshipitem'):
			profile.sponsorshipitem.add(SponsorshipItem.objects.get(name=item))
                profile.number_of_representatives = len(new_reps)
                profile.save()
                user.save()
                return HttpResponseRedirect('/dashboard')     
            else:
                print form.errors

        else:
            form = StudentProfileForm(request.POST, instance=user.studentprofile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = user
                if 'resume' in request.FILES:
                    profile.resume = request.FILES['resume']
                if 'picture-clear' in request.POST:
                    profile.picture = 'defaults/Student_icon.png'
                if 'picture' in request.FILES:
                    profile.picture = request.FILES['picture']
                profile.save()
                user.save()
                return HttpResponseRedirect('/dashboard')     
            else:
                print form.errors 

    context = {"form": form, 'rep_formset': rep_formset}

    return render(request, "pages/edit_profile.html", context)




# Company search form.
#
# Basically all it does is:
# Parse the CompanySearchForm object that was posted
# For every specified category, filter the entire company
# list by whatever parameters were given.

def company_search(request):
    context = RequestContext(request)

    # Set up query_results to be every company (that've paid of course)
    query_results = CompanyProfile.objects.filter(Q(has_submitted_payment = True)).order_by('company')
    company_search_form = CompanySearchForm()

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'GET' and 'company-search-posted' in request.session and not request.GET.get('page', None):
        request.session.pop('company-search-posted')
    if not request.method == 'POST' and 'company-search-posted' in request.session:
	request.method = 'POST'
    elif request.method == 'POST':
	if "company" in request.POST:
	    request.session['company_search'] = request.POST.getlist('company')[0]
	else:
	    request.session['company_search'] = ""
        if "days_attending" in request.POST:
	    request.session['days_search'] = request.POST.getlist('days_attending') 
        else:
	    request.session['days_search'] = ""
        if "grade_level_wanted" in request.POST:
	    request.session['grades_search'] = request.POST.getlist('grade_level_wanted')
	else:
	    request.session['grades_search'] = ""
        if "majors_wanted" in request.POST:
	    request.session['majors_search'] = request.POST.getlist('majors_wanted')
	else:
	    request.session['majors_search'] = ""

	request.session['company-search-posted'] = True

        # the reduce function is basically saying:
        # Query results is: The list of every company that contains
        # days_search[0], union with every company that contains 
        # days_search[1]... basically a bunch of unions.
    if request.method == 'POST':
	if 'company_search' in request.session and request.session['company_search']:
            query_results = query_results.filter(
                Q (company__icontains = request.session['company_search'] ) &
                Q (has_submitted_payment = True)
                ).order_by('company')
        if 'days_search' in request.session and request.session['days_search']:
	    query_results = query_results.filter(reduce(lambda x, y: x | y, [Q(days_attending__contains=day) for day in request.session['days_search']]))
        if 'grades_search' in request.session and request.session['grades_search']:
	    query_results = query_results.filter(reduce(lambda x, y: x | y, [Q(grade_level_wanted__contains=grade) for grade in request.session['grades_search']]))
        if 'majors_search' in request.session and request.session['majors_search']:
	    query_results = query_results.filter(reduce(lambda x, y: x | y, [Q(majors_wanted__contains=maj) for maj in request.session['majors_search']]))	    

    # Show 25 companies per page
    paginator = Paginator(query_results, 25) 
    page = request.GET.get('page')
    try:
        query_results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        query_results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        query_results = paginator.page(paginator.num_pages)
    return render_to_response('pages/company-search.html',
        {'query_results': query_results, 'company_search_form': company_search_form},
        context)

@user_passes_test(has_submitted_payment, login_url='/dashboard/prepaymentscreen/')
def student_search(request):
    context = RequestContext(request)
    query_results = StudentProfile.objects.all()
    student_search_form = StudentSearchForm()
    if request.method == 'GET' and 'student-search-posted' in request.session and not request.GET.get('page', None):
        request.session.pop('student-search-posted')
    if not request.method == 'POST' and 'student-search-posted' in request.session:
        request.method = 'POST'
    elif request.method == 'POST':
	request.session['student-search-posted'] = True
        if 'name' in request.POST and request.POST['name']:
	    request.session['name'] = request.POST['name']
	else:
	    request.session['name'] = ""
        if 'major_wanted' in request.POST and request.POST['major_wanted']:
            request.session['majors_search'] = request.POST.getlist('major_wanted')
	else:
	    request.session['majors_search'] = ""
        if 'grade_level_wanted' in request.POST and request.POST['grade_level_wanted']:
            request.session['grade_level_wanted'] = request.POST.getlist('grade_level_wanted')
	else:
	    request.session['grade_level_wanted'] = ""
        if request.POST['minimum_GPA']:
            request.session['minimum_GPA'] = request.POST['minimum_GPA']
        else:
	    request.session['minimum_GPA'] = 0
        if "open_to_relocation" in request.POST:
	    request.session['open_to_relocation'] = True
	else:
	    request.session['open_to_relocation'] = None
        
    if request.method == 'POST':
        query_results = StudentProfile.objects.filter(
            Q(first_name__icontains = request.session['name']) |
            Q(last_name__icontains = request.session['name']))

        if 'majors_search' in request.session and request.session['majors_search']:
            query_results = query_results.filter(
                reduce(lambda x, y: x | y, [Q(major__contains=maj) for maj in request.session['majors_search']]))

        if 'grade_level_wanted' in request.session and request.session['grade_level_wanted']:
            query_results = query_results.filter(
                reduce(lambda x, y: x | y, [Q(grade_level__contains=level) for level in request.session['grade_level_wanted']]))

        if 'minimum_GPA' in request.session and request.session['minimum_GPA']:
            query_results = query_results.filter(Q(GPA__gte = request.session['minimum_GPA']))

        if 'open_to_relocation' in request.session and request.session['open_to_relocation']:
            query_results = query_results.filter(open_to_relocation=True)

    paginator = Paginator(query_results, 50) # Show 50 students per page
    page = request.GET.get('page')
    try:
        query_results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        query_results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        query_results = paginator.page(paginator.num_pages)

    return render_to_response('pages/student_search.html',
        {"query_results": query_results, 'student_search_form': student_search_form},
        context)

# Upon clicking search results...
def company_redirect(request, uid):
    query_result = CompanyProfile.objects.get(id=uid)
    return render_to_response('pages/company-slug.html',
        {"company_profile": query_result,
        "user_profile": query_result.user},
        RequestContext(request))

def student_redirect(request, uid):
    query_result = StudentProfile.objects.get(id=uid)
    return render_to_response('pages/student-slug.html',
        {"student_profile": query_result,
        "user_profile": query_result.user},
        RequestContext(request))


# This is the view function for the main company map page.
# It serves one primary purpose: it allows staff members
# to update the table data live. It does this by:
#
#   First: Deleting all data in unselected cells
#   Second: Checking if the staff member attempted to
#           define a new cell
from django.contrib.admin.views.decorators import staff_member_required
@staff_member_required

def trans(s):
    count = ord(s[0]) - 64
    if len(s) > 1:
	count = count + 26

def reverse_trans(s):
    if s <=26:
	return chr(s+64)
    else:
	return chr(s+64-26)*2

def book_all_tables(request, day):
    print day
    # turn json post data into python dictionary
    table = json.loads(request.body)
    old = table["to_delete"]

    # coordinates do not need to be flipped for old data that has
    # already been processed
    old = [ (int(tuple.split('_')[1])-1 , int(tuple.split("_")[0])-1) for tuple in old]

    # Ping the database for the reservations we have so far
    reservations_table = ArmoryTableData.objects.get()
    jsonDec = json.decoder.JSONDecoder()
    if day == "friday":
        reservations = jsonDec.decode(reservations_table.friday_reservations)
    else:
        reservations = jsonDec.decode(reservations_table.saturday_reservations)

    # Reset the old values to 0
    for pair in old:
        reservations[pair[0]][pair[1]] = 0

    # Check if a staff member attempted to change a company's table
    if "company" in table and "bookings" in table:
        # Parse the JSON object for the company's user ID
        user_id = table["company"]

        # Use the ID to find the company's profle
        company = User.objects.get(id=user_id).companyprofile

        # Reformat the booking table (flip axis, subtract 1)
        bookings = table["bookings"]
        bookings = [(int(tuple.split('_')[1])-1 , int(tuple.split("_")[0])-1) for tuple in bookings]

        # Set each coordinated in the reservation table that is in
        # the booking table to the name of the company
        for booking in bookings:
            reservations[booking[0]][booking[1]] = company.company

        if day == "friday":
            company.friday_tables = json.dumps(bookings)
        else:
            company.saturday_tables = json.dumps(bookings)
        company.save()


    # Convert to json and save the data
    if day == "friday":
        reservations_table.friday_reservations = json.dumps(reservations)   
    else:
        reservations_table.saturday_reservations = json.dumps(reservations)    
    reservations_table.save()

    # Ayy we made it
    to_json = {"message":"success"}
    return HttpResponse(json.dumps(to_json), content_type='application/json')

# Small variaction of the book all tables functions above
# Takes a company name as input instead of ID
# Is a view designed to handle only one company page instead of all
@staff_member_required
def book_table(request, day):
    # turn json post data into python dictionary
    table = json.loads(request.body)
    bookings = table["bookings"]
    who = table["company"]
    old = table["to_delete"]
    company = CompanyProfile.objects.get(id=who)

    # Reformat it to be a list of integers take integers
    bookings = [ (int(tuple.split('_')[1])-1 , int(tuple.split("_")[0])-1) for tuple in bookings]

    # coordinates do not need to be flipped for old data that has
    # already been processed
    old = [ (int(tuple.split('_')[1])-1 , int(tuple.split("_")[0])-1) for tuple in old]

    # Ping the database for the reservations we have so far
    reservations_table = ArmoryTableData.objects.get()
    jsonDec = json.decoder.JSONDecoder()
    if day == "friday":
        reservations = jsonDec.decode(reservations_table.friday_reservations)
    else:
        reservations = jsonDec.decode(reservations_table.saturday_reservations)

    # Reset the old values to 0
    for pair in old:
        reservations[pair[0]][pair[1]] = 0

    # Place the new values
    for booking in bookings:
        reservations[booking[0]][booking[1]] = company.company

    # Convert to json and save the data
    # Convert to json and save the data
    if day == "friday":
        reservations_table.friday_reservations = json.dumps(reservations)
        company.friday_tables = json.dumps(bookings)   
    else:
        reservations_table.saturday_reservations = json.dumps(reservations)
        company.saturday_tables = json.dumps(bookings)  
    reservations_table.save()
    company.save()

    # Ayy we made it
    to_json = {"message":"success"}
    return HttpResponse(json.dumps(to_json), content_type='application/json')

def get_bookings(request, day):
    jsonDec = json.decoder.JSONDecoder()
    if day == "friday":
        reservations_table_json = ArmoryTableData.objects.get().friday_reservations
    else:
        reservations_table_json = ArmoryTableData.objects.get().saturday_reservations    
    reservations_table = jsonDec.decode(reservations_table_json)
    booked = []
    for x, column in enumerate(reservations_table):
        for y, table in enumerate(column):
            if table:
                booked.append({"seat_id":str(y+1)+"_"+str(x+1)})

    return HttpResponse( json.dumps({"bookings": booked}) )

def get_company_booking(request,uid,day):
    jsonDec = json.decoder.JSONDecoder()
    company = User.objects.get(id=uid).companyprofile
    if day == "friday":
        reservations_table_json = company.friday_tables
    else:
        reservations_table_json = company.saturday_tables
    reservations_table = jsonDec.decode(reservations_table_json)
    booked = []
    hashable = []
    for table in reservations_table:
        hashable.append( (table[1]+1, table[0]+1) )
        booked.append( {"seat_id": str(table[1]+1)+"_"+str(table[0]+1) })

    others_booked = []
    if day == "friday":
        reservations_table_json = ArmoryTableData.objects.get().friday_reservations
    else:
        reservations_table_json = ArmoryTableData.objects.get().saturday_reservations 
    reservations_table = jsonDec.decode(reservations_table_json)
    for x, column in enumerate(reservations_table):
        for y, table in enumerate(column):
            if table and (y+1, x+1) not in hashable:
                others_booked.append({"seat_id":str(y+1)+"_"+str(x+1)})

    logo_url = ""
    try:
	logo_url = company.logo.url
    except ValueError:
	logo_url = "uploads/default_icons/Company_icon.png"    
 
    return HttpResponse( json.dumps({"bookings": booked, "others":others_booked, 
        "companyname":company.company, "company_bio":company.company_bio,
        "days_attending":"<br>".join(company.days_attending), 
        "logo":logo_url, "grade_level_wanted":"<br>".join(company.grade_level_wanted), 
        "majors_wanted": "<br>".join(company.majors_wanted) }) )

def armory_manipulation(request):
    try:
        company_list = CompanyProfile.objects.filter(has_submitted_payment = True).order_by('company')
    except:
        company_list = []
    return render_to_response("pages/armory_layout.html", {"company_list":company_list}, RequestContext(request))

def pay_success(request):
     render_to_response('pages/success.html',{},RequestContext(request))

@login_required
def view_that_asks_for_money(request):
    context = RequestContext(request)
    company = request.user.companyprofile
    paypal_account, item_name, bill = get_bill(company)
    company.total_bill = bill
    company.save()

    # career_fair_year was put here to correct the problem where 
    # invoices were not unique each year so companies had problem paying through PayPal.
    # This should be updated every year to ensure companies don't have a problem.
    career_fair_year = "2017"

    # What you want the button to do.
    paypal_dict = {
        "business": paypal_account,
        "amount": str(bill),
        "item_name": "39th NSBE/SHPE Career Fair Registration Fee",
        "invoice": "invoice_1_"+request.user.companyprofile.company+"_"+career_fair_year,
        "notify_url": NGROK+"/paypal-ipn/",
        "return_url": NGROK+"/return_paypal/",
        "cancel_return": NGROK+"/dashboard/prepaymentscreen/",
        "custom": request.user.id,  # Custom command to correlate to some function later (optional)
    }
    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    
    #Find the paypal info object to render some price information on the prepayment screen
    paypalinfo = PayPalInfo.objects.all()[0]

    context = {"form": form, "paypal":paypalinfo}
    return render(request, "pages/prepaymentscreen.html", context)

def process_me(request):
    valid_ipn_received.connect(show_me_the_money)

@csrf_exempt
def return_me(request):
    print "succcess"
    return render_to_response('pages/success.html',{},RequestContext(request))
