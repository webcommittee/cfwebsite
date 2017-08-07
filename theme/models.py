from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.encoding import python_2_unicode_compatible
from mezzanine.conf import settings
from django import forms
import django

from django.utils.translation import ugettext_lazy as _
import uuid

from mezzanine.core.fields import FileField, RichTextField
from mezzanine.core.models import RichText, Orderable, Slugged
from mezzanine.pages.models import Page
from mezzanine.forms.models import Form
from mezzanine.forms import fields
from mezzanine.utils.models import upload_to
from multiselectfield import MultiSelectField
from customutils import ContentTypeRestrictedFileField
#
#
# REGISTRATION FORMS:


# VOLUNTEER_CHOICES, DAY_CHOICES, MAJOR_CHOICES, MINOR_CHOICES, and GRADE_LEVEL_CHOICES
#  are all multiple choice fields
# for company and student registration.  Each is a tuple because it needs both
# a database representation (the left value) and the value that gets rendered
#(the righ value), and I make it so that the value and the database entry are the same.
VOLUNTEER_CHOICES = (('Armory', 'Armory'),
                    ('Food', 'Food'),
                    ('Something else', 'Something else'))

DAY_CHOICES = (('Friday', 'Friday'),
                ('Saturday', 'Saturday'))

MAJOR_CHOICES = (('Aeronautical Engineering', 'Aeronautical Engineering'),
                ('Applied Physics', 'Applied Physics'),
                ('Architecture', 'Architecture'),
                ('Biochemistry and Biophysics', 'Biochemistry and Biophysics'),
                ('Bioinformatics and Molecular Biology', 'Bioinformatics and Molecular Biology'),
                ('Biology', 'Biology'),
                ('Biomedical Engineering', 'Biomedical Engineering'),
                ('Building Science', 'Building Science'),
                ('Business and Management', 'Business and Management'),
                ('Chemical Engineering', 'Chemical Engineering'),
                ('Chemistry', 'Chemistry'),
                ('Civil Engineering', 'Civil Engineering'),
                ('Cognitive Science', 'Cognitive Science'),
                ('Communication', 'Communication'),
                ('Computer and Systems Engineering', 'Computer and Systems Engineering'),
                ('Computer Science', 'Computer Science'),
                ('Design, Innovation, and Society', 'Design, Innovation, and Society'),
                ('Economics', 'Economics'),
                ('Electrical Engineering', 'Electrical Engineering'),
                ('Electronic Arts', 'Electronic Arts'),
                ('Electronic Media, Arts, and Communication', 'Electronic Media, Arts, and Communication'),
                ('Environmental Engineering', 'Environmental Engineering'),
                ('Environmental Science', 'Environmental Science'),
                ('Games and Simulation Arts and Sciences', 'Games and Simulation Arts and Sciences'),
                ('Geology', 'Geology'),
                ('Hydrogeology', 'Hydrogeology'),
                ('Industrial and Management Engineering', 'Industrial and Management Engineering'),
                ('Information Technology and Web Science', 'Information Technology and Web Science'),
                ('Interdisciplinary Science', 'Interdisciplinary Science'),
                ('Materials Engineering', 'Materials Engineering'),
                ('Mathematics', 'Mathematics'),
                ('Mechanical Engineering', 'Mechanical Engineering'),
                ('Nuclear Engineering', 'Nuclear Engineering'),
                ('Philosophy', 'Philosophy'),
                ('Physics', 'Physics'),
                ('Psychology', 'Psychology'),
                ('Science, Technology, and Society', 'Science, Technology, and Society'),
                ('Sustainability Studies', 'Sustainability Studies'))

MINOR_CHOICES = (('------------','-----------'),
                    ('Acoustics', 'Acoustics'),
                    ('Air and Space Leadership Studies', 'Air and Space Leadership Studies'),
                    ('Architecture', 'Architecture'),
                    ('Astrobiology', 'Astrobiology'),
                    ('Astronomy', 'Astronomy'),
                    ('Astrophysics', 'Astrophysics'),
                    ('Biochemistry', 'Biochemistry'),
                    ('Biology', 'Biology'),
                    ('Biophysics', 'Biophysics'),
                    ('Brain and Brain Behavior', 'Brain and Brain Behavior'),
                    ('Chemistry', 'Chemistry'),
                    ('Civil Engineering', 'Civil Engineering'),
                    ('Chinese', 'Chinese'),
                    ('Cognition', 'Cognition'),
                    ('Communication', 'Communication'),
                    ('Community and Health Psychology', 'Community and Health Psychology'),
                    ('Computer Science', 'Computer Science'),
                    ('Computer and Systems Engineering', 'Computer and Systems Engineering'),
                    ('Electrical Power Engineering', 'Electrical Power Engineering'),
                    ('Electrical Engineering', 'Electrical Engineering'),
                    ('Electronic Arts', 'Electronic Arts'),
                    ('Electronic Media, Arts, and Communication', 'Electronic Media, Arts, and Communication'),
                    ('Energy', 'Energy'),
                    ('Entrepreneurship', 'Entrepreneurship'),
                    ('Environmental Engineering', 'Environmental Engineering'),
                    ('Environmental Science', 'Environmental Science'),
                    ('Finance', 'Finance'),
                    ('Games and Simulation Arts and Sciences', 'Games and Simulation Arts and Sciences'),
                    ('Geology', 'Geology'),
                    ('Game Studies', 'Game Studies'),
                    ('Gender, Science and Technology', 'Gender, Science and Technology'),
                    ('History of Architecture', 'History of Architecture'),
                    ('Hydrogeology', 'Hydrogeology'),
                    ('Human-Computer Interaction', 'Human-Computer Interaction'),
                    ('Human Factors in Psychology', 'Human Factors in Psychology'),
                    ('Industrial/Organizational Psychology', 'Industrial/Organizational Psychology'),
                    ('Industrial and Management Engineering', 'Industrial and Management Engineering'),
                    ('Lighting', 'Lighting'),
                    ('Literature', 'Literature'),
                    ('Logic, Computation and Mind', 'Logic, Computation and Mind'),
                    ('Management', 'Management'),
                    ('Marketing', 'Marketing'),
                    ('Materials Engineering', 'Materials Engineering'),
                    ('Mathematics', 'Mathematics'),
                    ('Military Studies', 'Military Studies'),
                    ('Music', 'Music'),
                    ('Origins of Life', 'Origins of Life'),
                    ('Philosophy of Human Values and Society', 'Philosophy of Human Values and Society'),
                    ('Philosophy of Logic, Computation and Mind', 'Philosophy of Logic, Computation and Mind'),
                    ('Philosophy of Science and Technology', 'Philosophy of Science and Technology'),
                    ('Philosophy', 'Philosophy'),
                    ('Physics', 'Physics'),
                    ('Professional Writing', 'Professional Writing'),
                    ('Psychology', 'Psychology'),
                    ('Science, Technology, and Society', 'Science, Technology, and Society'),
                    ('Social Psychology', 'Social Psychology'),
                    ('Sports Psychology', 'Sports Psychology'),
                    ('Sustainability Studies', 'Sustainability Studies'),
                    ('Studio Arts', 'Studio Arts'),
                    ('Technology Commercialization and Entrepreneurship', 'Technology Commercialization and Entrepreneurship'),
                    )

GRADE_LEVEL_CHOICES = (('Freshman', 'Freshman'),
                       ('Sophomore', 'Sophomore'),
                       ('Junior', 'Junior'),
                       ('Senior', 'Senior'),
                       ('Graduate', 'Graduate'),
                       ('PhD', 'PhD'))

MAJOR_CHOICES_FLAT = [major[0] for major in MAJOR_CHOICES]

#There are two model categories:  -Pages and their corresponding "sub models"
#                                 -Profiles and other user data

# Page models would have stuff such as "header" and "blurb" and what not so
# that users using the content management system (mezzanine) would be able
# to edit that field.

# The SponsorUsPage, for example has a page_header field, a page blurb, etc
# and it also has SponsorshipPackages and SponsorshipItem that are rendered to
# that page and can also be accessed and set in the CMS.

#
#
# SPONSORSHIP PAGE:
#

class SponsorUsPage(Page, RichText):
    misc_items = models.CharField(max_length=100)
    misc_items_blurb = RichTextField(max_length=3000, help_text="Some paragraph of text above the segment of the page where the sponsorship packages are listed")
    page_header = models.CharField(max_length=100, default="Sponoorship")
    page_blurb = RichTextField(max_length=4000, help_text="Some paragraph explaining the beautiful of sponsorhsips")
    contact = RichTextField(max_length=1000)

class SponsorshipPackage(models.Model):
    level = models.IntegerField(help_text="This is the ranking of this package. Each Sponsorship package should be ranked from worst to best.  1 is worst, highest is best.")
    title = models.CharField(help_text="What do you name this package? This will appear on the sponsorus page", max_length=100)
    description = RichTextField(help_text="In detail, describe the amenities of the package.  Be sure to format it nicely because whatever you write here will be displayed on the sponsor us page.")
    price = models.IntegerField(help_text="Finally, put the price.")
    num_free_tables = models.IntegerField(help_text="Number of free tables the company would recieve for picking this sponsorship")
    num_free_reps = models.IntegerField(help_text="Number of free reps the company recieve for this package")
    sponsoruspage = models.ForeignKey(SponsorUsPage, related_name="sponsorship_package")
    discount = models.IntegerField(help_text="Some amount to be subtracted from their end total? (free registration or something)", default=0)

    def __unicode__ (self):
        return self.title

class SponsorshipItem(models.Model):
    name = models.CharField(help_text="The name of this item", max_length=200)
    price = models.IntegerField(help_text="The price of this item")

    def __unicode__ (self):
	return self.name
#
#
# Student profile
#

from .validators import validate_file_extension
class StudentProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    phone_number = models.CharField(blank=True, max_length=14)
    grade_level = MultiSelectField(choices=GRADE_LEVEL_CHOICES, max_choices=1, blank=True)
    major = MultiSelectField(choices=MAJOR_CHOICES, max_choices=2, blank=True)
    minor = MultiSelectField(choices=MINOR_CHOICES, max_choices=1, blank=True)
    resume = models.FileField(upload_to='resumes', blank=True)
    picture = models.ImageField(upload_to='uploads/student_images', blank=True)
    hometown = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    open_to_relocation = models.BooleanField(default=False, blank=True, help_text="Open to relocation?")
    GPA = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    bio = models.TextField(max_length=1000, blank=True)
    website = models.CharField(max_length=500, blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.last_name + ", " + self.first_name

    class Meta:
        get_latest_by = 'creation_date'

class StudentSearchFormModel(models.Model):
    name = models.CharField(max_length=100, blank=True)
    grade_level_wanted = MultiSelectField(choices=GRADE_LEVEL_CHOICES, blank=True)
    major_wanted = MultiSelectField(choices=MAJOR_CHOICES, blank=True)
    open_to_relocation = models.BooleanField(default=False, blank=True)
    minimum_GPA = models.DecimalField(max_digits=3, decimal_places=2, null=True)


#
#
# Company profile

class CompanyRep(models.Model):
   rep = models.CharField(max_length=100)
   is_alumni = models.BooleanField(default=False)
   days_attending = MultiSelectField(choices=DAY_CHOICES)
   user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
   company = models.CharField(max_length=60, blank=True, null=True)
   is_present = models.BooleanField(default=False)

   def __unicode__(self):
       return self.rep


class CompanyProfile(models.Model):
    company = models.CharField(_("Company name"),
        max_length=60)
    user = models.OneToOneField(User)
    phone_number = models.CharField(_("Phone number"),
     max_length=16, blank=True)
    company_website = models.CharField(_("Company website"),
        max_length=1000, blank=True)
    logo = models.ImageField(_("Company logo"),
        upload_to='uploads/company_images', blank=True)
    days_attending = MultiSelectField(_("Days attending"),
        choices=DAY_CHOICES)
    majors_wanted = MultiSelectField(_("Majors wanted"),
        choices=MAJOR_CHOICES)
    grade_level_wanted = MultiSelectField(_("Grade level wanted"),
        choices=GRADE_LEVEL_CHOICES)
    company_bio = models.TextField(_("Company bio"),
        max_length=1000, blank=True)
    has_submitted_payment = models.BooleanField(_("Has submitted payment"),
        default=False)
    friday_tables = models.TextField(_("Friday table locations"),
        default='[]')
    friday_number_of_tables = models.IntegerField(_("Friday # of tables"),
        default=0)
    saturday_tables = models.TextField(_("Saturday table locations"),
        default='[]')
    saturday_number_of_tables = models.IntegerField(_("Saturday # of tables"),
        default=0)
    creation_date = models.DateTimeField(_("Creation time"),
        auto_now_add=True, null=True)
    updated_at = models.DateTimeField(_("Last updated"),
        auto_now=True, null=True)
    reps = models.ManyToManyField(
        CompanyRep, _("Representatives+"))
    reps_alumni = models.ManyToManyField(
        CompanyRep, _("Alumni reps+"),blank=True)
    number_of_representatives = models.IntegerField(_("Number of representatives"),
        default=1)
    friday_representatives = models.ManyToManyField(CompanyRep, _("Fridays reps+"),
        blank=True)
    saturday_representatives = models.ManyToManyField(CompanyRep, _("Saturday reps+"),
        blank=True)
    number_of_tables = models.IntegerField(_("Number of tables"),
        default=0)
    total_bill = models.IntegerField(_("Total bill"),null=True,
        default=500)
    interview_rooms_friday = models.IntegerField(null=True, default=0)
    interview_friday_from = models.CharField(null=True, blank=True, max_length=15)
    interview_friday_to = models.CharField(null=True, blank=True, max_length=15)
    interview_rooms_saturday = models.IntegerField(null=True, default=0)
    interview_saturday_from = models.CharField(null=True, blank=True, max_length=15)
    interview_saturday_to = models.CharField(null=True, blank=True,max_length=15)
    tables = models.TextField(_("Staff assigned tables"),default='[]', null=True, blank=True)
    is_non_profit = models.BooleanField(_("Is non-profit"),default=False)
    sponsor = models.CharField(_("Sponsorship choice"),max_length=100,
        blank=True)
    sponsorshipitem = models.ManyToManyField(SponsorshipItem, _("Sponsorship item choices+"), blank=True)
    def __unicode__ (self):
        return self.company

from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete, sender=CompanyProfile)
def delete_table(sender, instance, **kwargs):
    if sender == CompanyProfile:
        import json
        reservations = ArmoryTableData.objects.get().friday_reservations
        friday = json.loads(instance.friday_tables)
        saturday = json.loads(instance.saturday_tables)
        reservations =json.loads(reservations)
        for table in friday:
            print table
            reservations[table[1]][table[0]] = None
        reservations = ArmoryTableData.objects.get().saturday_reservations
        reservations = json.loads(reservations)
        for table in saturday:
            reservations[table[1]][table[0]] = None


#
#
# REGISTRATION PAGE:

class RegistrationPage(Page, RichText):

    button_text = models.CharField(_("Button text"), max_length=50, blank=True)
    response = RichTextField(_("Response"))
    send_email = models.BooleanField(_("Send email to user"), default=True,
        help_text=_("To send an email to the email address supplied in "
                    "the form upon submission, check this box."))
    email_from = models.EmailField(_("From address"), max_length=254,
        help_text=_("The address the email will be sent from"), blank=True)
    email_subject = models.CharField(_("Subject"), max_length=200, blank=True)
    email_message = RichTextField(_("Message"), blank=True,
        help_text=_("Emails sent based on the above options will contain "
                    "each of the form fields entered. You can also enter "
                    "a message here that will be included in the email."))
    email_copies = models.CharField(_("Send email to others"), blank=True,
        help_text=_("Provide a comma separated list of email addresses "
                    "to be notified upon form submission. Leave blank to "
                    "disable notifications."),
        max_length=200)
    attachment = models.FileField(_("Maybe a PDF with some information?"),
        upload_to='uploads/company_images',
        blank=True,
        help_text=_("A file field.  Feel free to add whatever you want to this email."))
    invoice_template_text = models.FileField(_("Invoice Text Template"),
        upload_to='uploads/templates',
        blank=True,
        help_text=_("Text template of invoice in case html version does not render"))
    invoice_template_html = models.FileField(_("Invoice HTML Template"),
        upload_to='uploads/templates',
        blank=True,
        help_text=_("Should be identical to the text template except with added html"))
    google_maps_api_key = models.CharField(max_length=200, blank=True,
        help_text="Google how to obtain a google maps key for the location mueller center and past it here")
    text_under_map = models.TextField(max_length=1000, blank=True)
    show_sponsorship_items = models.BooleanField(default=True)
    class Meta:
        verbose_name = _("Registration Page")
        verbose_name_plural = _("Registration Pages")

#
# ABOUT PAGE:
#

class AboutPage(Page, RichText):
    super_heading = models.CharField(max_length= 100)
    heading1 = models.CharField(max_length= 50,
        help_text="Header for column 1")
    heading2 = models.CharField(max_length= 50,
        help_text="Header for column 2")
    heading3 = models.CharField(max_length= 50,
        help_text="Header for column 3")
    LeftColumn = RichTextField(max_length= 3000,
        help_text="Blurb under heading1",
        default="")
    MidColumn = RichTextField(max_length= 3000,
        help_text="Blurb under heading2",
        default="")
    RightColumn = RichTextField(max_length= 3000,
        help_text="Blurb under heading3",
        default="")
    heading4 = models.CharField(max_length= 50,
        help_text="Header for bottom blurb",
        default= "Our Team")
    BottomRow = RichTextField(max_length=3000,
        help_text="Blurb under heading4",
        default="")

class StaffProfile(Orderable):
    '''
    A slide in a slider connected to a HomePage
    '''
    aboutpage = models.ForeignKey(AboutPage, related_name="aboutpage", null=True)
    name = models.CharField(max_length = 100, help_text="Enter the name of the staff memeber here")
    position = models.CharField(max_length = 100, help_text="Enter their position among the career fair staff")
    bio = RichTextField(max_length = 1000, help_text="Enter a short bio of that person and their duties")
    image = FileField(verbose_name=_("Image"),
        upload_to=upload_to("theme.Slide.image", "Headshots"),
        format="Image", max_length=255, null=True, blank=True)
    def __unicode__(self):
        return self.name

class Committee(Orderable):
    committee_members = models.ManyToManyField(StaffProfile, _("Committee"))
    committee_name = models.CharField(max_length = 100, help_text="Name of committee", default = "Committee name")
    aboutpage = models.ForeignKey(AboutPage, related_name="committee")



#
#
# AGENDA PAGE:
#

class AgendaPage(Page, RichText):
    heading = models.CharField(max_length=200,
        help_text="Put title here or something")
    friday = RichTextField(max_length=30000, help_text="Enter a nicely formatted schedule of friday here")
    saturday = RichTextField(max_length=30000, help_text="Enter a nicely formatted schedule of saturday here")

#
#
# CONTACT PAGE:
#

class ContactPage(Page, RichText):
    heading = models.CharField(max_length=200,
        help_text="Put title here or something")
    contact_info = RichTextField(max_length=30000, help_text="Enter a nicely formatted contact page here")

class PricingPage(Page, RichText):
    heading = models.CharField(max_length=200,
        help_text="Put title here or something")
    pricing_info = RichTextField(max_length=30000, help_text="Enter a nicely formatted pricing page here, complete with any sponsorship information you could think of.")


class TipPage(Page, RichText):
    body = RichTextField(verbose_name=_("Body"),
        help_text="Insert tips here",
	default="aaa")

#
# HOMEPAGE:
#

class HomePage(Page, RichText):
    '''
    A page representing the format of the home page
    '''
    heading = models.CharField(max_length=200,
        help_text="Put title here or something")
    hptime = models.CharField(max_length=200,
        help_text="Time, Data, Location",
        default= "00:00:00")
    hpdate = models.CharField(max_length=200,
        help_text="Date",
        default= "00/00/00")
    hploc = models.CharField(max_length=200,
        help_text="Location",
        default="Aaa, Aaa")
    subheading = RichTextField(max_length=1000,
        help_text="Some text explaining what the career fair is",
        default= "Write something here already")
    IconText1 = models.CharField(max_length = 200,
        default = "IconText1", blank=True)
    IconTitle1 = models.CharField(max_length = 50,
        default = "IconTitle1", blank=True)
    IconText2 = models.CharField(max_length = 200,
        default = "IconText2", blank=True)
    IconTitle2 = models.CharField(max_length = 50,
        default = "IconTitle2", blank=True)
    IconText3 = models.CharField(max_length = 200,
        default = "IconText3", blank=True)
    IconTitle3 = models.CharField(max_length = 50,
        default = "IconTitle3", blank=True)
    IconText4 = models.CharField(max_length = 200,
        default = "IconText4", blank=True)
    IconTitle4 = models.CharField(max_length = 50,
        default = "IconTitle4", blank=True)
    IconUrl1 = models.CharField(max_length = 1000,
        default = "#")
    IconUrl2 = models.CharField(max_length = 1000,
        default = "#")
    IconUrl3 = models.CharField(max_length = 1000,
        default = "#")
    IconUrl4 = models.CharField(max_length = 1000,
        default = "#")
    featured_companies_heading = models.CharField(max_length=200,
        default = "Featured Companies")
    announcement_header = models.CharField(max_length = 30,
        help_text = "Title for announcements field",
        default = "Announcements")
    content_heading = models.CharField(max_length=200,
        default="About us!")
    latest_posts_heading = models.CharField(max_length=200,
        default="Latest Posts")
    misc_info_header = models.CharField(max_length = 30,
        help_text = "Title for misc info field",
        default = "About us")
    misc_info_body = RichTextField(max_length = 2000,
        help_text = "Body for misc info field",
        default = "About us")

    class Meta:
        verbose_name = _("Home page")
        verbose_name_plural = _("Home pages")

class FAQPage(Page, RichText):
    heading = models.CharField(max_length=500, help_text = "Put title here")
    class Meta:
        verbose_name = _("Faq page")
        verbose_name_plural = _("Faq Pages")


class Question(Orderable):
    faqpage = models.ForeignKey(FAQPage, related_name="question")
    question = models.CharField(_("Question"), max_length = 500,  default = "Question")
    answer = RichTextField(_("Answer"), null=True)

class ArmoryTableData(models.Model):
    friday_reservations = models.TextField(null=True)
    saturday_reservations = models.TextField(null=True)

class Slide(Orderable):
    '''
    A slide in a slider connected to a HomePage
    '''
    homepage = models.ForeignKey(HomePage, related_name="slides")
    image = FileField(verbose_name=_("Image"),
        upload_to=upload_to("theme.Slide.image", "slider"),
        format="Image", max_length=255, null=True, blank=True)


class FeaturedCompany(Orderable):
    '''
    A showcase of featured company logos connected to a HomePage
    '''
    homepage = models.ForeignKey(HomePage, related_name="featured_companies")
    image = FileField(verbose_name=_("Image"),
        help_text="A square, transparent image (or white background) to represent the company on the frontpage slider.  Make sure it's a square.",
        upload_to=upload_to("theme.FeaturedCompany.image", "Featured Companies"),
        format="Image", max_length=255, null=True, blank=True)
    link_to = models.CharField(max_length = 1000,
        help_text = "A link to the company's application site",
        default = "http://")



class Announcement(Orderable):
    '''
    A slide of all the latest announcements posted by site admin
    '''
    homepage = models.ForeignKey(HomePage, related_name="announcements")
    date = models.CharField(max_length = 6,
        help_text = "Date (no year) DD MMM ",
        default = "01 Jan")
    year = models.CharField(max_length = 5,
        help_text = "Year YYYY",
        default = "0000")
    announcement_title = models.CharField(max_length = 100,
        help_text = "Title of your announcement post",
        default = "Announcement here!")
    announcement_text = models.TextField(max_length = 500,
        help_text = "Type your new announcement here",
        default = "")
    author = models.CharField(max_length = 100,
        help_text = "Type your name as you want it to appear",
        default = "")


class IconBlurb(Orderable):
    '''
    An icon box on a HomePage
    '''
    homepage = models.ForeignKey(HomePage, related_name="blurbs")
    icon = FileField(verbose_name=_("Image"),
        upload_to=upload_to("theme.IconBlurb.icon", "icons"),
        format="Image", max_length=255)
    title = models.CharField(max_length=200)
    content = models.TextField()
    link = models.CharField(max_length=2000, blank=True,
        help_text="Optional, if provided clicking the blurb will go here.")



# This is the class that allows people to edit the price and account names and what not
# from the front end
class PayPalInfo(models.Model):
    email = models.EmailField(default="", help_text="The email account associated with whatever paypal account you plan on using")
    friday_price = models.IntegerField(help_text="Friday's base fee.  THis includes the registration fee, one table, two reps, breakfast and lunch", default = 560)
    saturday_price = models.IntegerField(help_text="Saturday's base fee.  Also includes registration fee, one table, two reps, etc", default = 560)
    weekend_price = models.IntegerField(help_text="Discounted price for companies attending both days", default=1050)
    price_per_rep = models.IntegerField(help_text="Price per representative beyond the first two", default = 100)
    price_per_alumni_rep = models.IntegerField(help_text="Price per RPI alumni representative", default=100)
    price_per_table = models.IntegerField(help_text="Price per table beyond the first", default=125)
    item_name = models.CharField(help_text="What is the name of the item/service they are buying?",
        max_length=400,
        default="SHPE Company Career Fair Registration Fee 2017")
    class Meta:
        verbose_name = _("PayPal Info")
        verbose_name_plural = _("PayPal Info")

    def __unicode__(self):
        return self.email

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the business field request. (The user could tamper
        # with those fields on payment form before send it to PayPal)
        if ipn_obj.receiver_email != PayPalInfo.objects.get().email:
            # Not a valid paymen
	    print ipn_obj.receiver_email, PayPalInfo.objects.get().email
            return

        # ALSO: for the same reason, you need to check the amount
        # received etc. are all what you expect.

        # Undertake some action depending upon `ipn_obj`.
        user_id = ipn_obj.custom
        company = User.objects.get(id=user_id).companyprofile
        company.has_submitted_payment = True
        company.save()
        print "my boy got saved", User.objects.get(id=user_id).companyprofile.has_submitted_payment
    else:
        print "uh oh send an email"
        print ipn_obj.payment_status
        #...

valid_ipn_received.connect(show_me_the_money)
