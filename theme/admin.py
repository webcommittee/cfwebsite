from __future__ import unicode_literals
from future.builtins import open, bytes
import csv

from django.contrib import admin
from django.core.files.storage import FileSystemStorage
from django.utils.translation import ungettext, ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse

from datetime import datetime

from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.messages import info

from models import HomePage
from models import AboutPage
from models import RegistrationPage
from models import SponsorUsPage
from models import FAQPage
from models import AgendaPage
from models import ContactPage
from models import PricingPage
from models import TipPage

from models import Slide
from models import IconBlurb
from models import FeaturedCompany
from models import Announcement
from models import StaffProfile
from models import Question
from models import Committee
from models import CompanyRep

from models import StudentProfile
from models import CompanyProfile
from models import PayPalInfo
from models import SponsorshipPackage
from models import SponsorshipItem

from forms import EntriesForm

from mezzanine.conf import settings
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

#
# USER EXTENSIONS:
#

class CompanyProfileInLine(admin.StackedInline):
	model = CompanyProfile
	can_delete = False
	verbose_name_plural = "companyprofile"

class StudentProfileInLine(admin.StackedInline):
	model = StudentProfile
	can_delete = True
	verbose_name_plural = "studentprofile"

class UserAdmin(BaseUserAdmin):
	inlines = (CompanyProfileInLine,StudentProfileInLine)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)



#
#
# HOMEPAGE:
#

class SlideInline(TabularDynamicInlineAdmin):
	model = Slide

class IconBlurbline(TabularDynamicInlineAdmin):
	model = IconBlurb

class FeaturedCompanyline(TabularDynamicInlineAdmin):
	model = FeaturedCompany

class AnnouncementLine(TabularDynamicInlineAdmin):
	model = Announcement

class HomePageAdmin(PageAdmin):
	inlines = (SlideInline, IconBlurbline, FeaturedCompanyline, AnnouncementLine)

#
#
# ABOUT PAGE:
#

class StaffProfileLine(TabularDynamicInlineAdmin):
	model = StaffProfile

class CommitteeInline(TabularDynamicInlineAdmin):
	model = Committee

class AboutPageAdmin(PageAdmin):
	inlines = (CommitteeInline, StaffProfileLine)

#
#
# REGISTRATION PAGES:
#

class SponsorshipPackageInline(TabularDynamicInlineAdmin):
    model = SponsorshipPackage

class SponsorUsPageAdmin(PageAdmin):
    inlines = (SponsorshipPackageInline,)

from mezzanine.utils.urls import admin_url, slugify
from io import BytesIO, StringIO
from mezzanine.utils.static import static_lazy as static
from csv import writer
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

class RegistrationPageAdmin(PageAdmin):
    """
    Admin class for the Form model. Includes the urls & views for exporting
    form entries as CSV and downloading files uploaded via the forms app.
    """

    class Media:
        css = {"all": (static("mezzanine/css/admin/form.css"),)}

    # inlines = (FieldAdmin,)
    list_display = ("title", "status", "email_copies",)
    list_display_links = ("title",)
    list_editable = ("status", "email_copies")
    list_filter = ("status",)
    search_fields = ("title", "content", "response", "email_from",
                     )
    #fieldsets = form_fieldsets

    def get_urls(self):
        """
        Add the entries view to urls.
        """
        urls = super(RegistrationPageAdmin, self).get_urls()
        extra_urls = [
            url("^(?P<form_id>\d+)/entries/$",
                self.admin_site.admin_view(self.entries_view),
                name="form_entries"),
        ]
        return extra_urls + urls

    def entries_view(self, request, form_id):
        """
        Displays the form entries in a HTML table with option to
        export as CSV file.
        """
        if request.POST.get("back"):
            change_url = admin_url(RegistrationPage, "change", form_id)
            return HttpResponseRedirect(change_url)
        form = get_object_or_404(RegistrationPage, id=form_id)
        entries_form = EntriesForm(form, request, request.POST or None)
        #delete_entries_perm = "%s.delete_formentry" % FormEntry._meta.app_label
        #can_delete_entries = request.user.has_perm(delete_entries_perm)
        submitted = entries_form.is_valid()
        if submitted:
            if request.POST.get("export"):
                response = HttpResponse(content_type="text/csv")
                timestamp = slugify(datetime.now().ctime())
                fname = "%s-%s.csv" % (form.slug, timestamp)
                header = "attachment; filename=%s" % fname
                response["Content-Disposition"] = header
                queue = StringIO()
                delimiter = settings.FORMS_CSV_DELIMITER
                try:
                    csv = writer(queue, delimiter=delimiter)
                    writerow = csv.writerow
                except TypeError:
                    queue = BytesIO()
                    delimiter = bytes(delimiter, encoding="utf-8")
                    csv = writer(queue, delimiter=delimiter)
                    writerow = lambda row: csv.writerow([c.encode("utf-8")
                        if hasattr(c, "encode") else c for c in row])
                writerow(entries_form.columns())
                for row in entries_form.rows(csv=True):
                    writerow(row)
                data = queue.getvalue()
                response.write(data)
                return response
            elif request.POST.get("delete"):
                selected = request.POST.getlist("selected")
                if selected:
                    entries = CompanyProfile.objects.filter(id__in=selected)
                    count = entries.count()
                    if count > 0:
                        entries.delete()
                        message = ungettext("1 entry deleted",
                                            "%(count)s entries deleted", count)
                        info(request, message % {"count": count})
        template = "admin/forms/entries.html"
        context = {"title": _("View Entries"), "entries_form": entries_form,
                   "opts": self.model._meta, "original": form,
                   "can_delete_entries": True,
                   "submitted": submitted}
        return render_to_response(template, context, RequestContext(request))

#
#
# FAQ Page:
#

class QuestionInLine(TabularDynamicInlineAdmin):
    model = Question

class FAQPageAdmin(PageAdmin):
    inlines=(QuestionInLine,)

class StudentAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name']
    list_max_show_all = 10000 

class CompanyAdmin(admin.ModelAdmin):
    search_fields = ['company']
    list_display = ['company', 'user', 'days_attending', 'has_submitted_payment', 'total_bill']

class CompanyRepAdmin(admin.ModelAdmin):
    search_fields = ['rep', 'company']
    list_display = ['rep', 'company', 'days_attending', 'is_present']
    actions = ['make_attend', 'reset_attendance',  'export_selected_objects']
    list_max_show_all = 1000
    def make_attend(self, request, queryset):
	for rep in queryset.all():
	    rep.is_present = not rep.is_present
	    rep.save()
   
    def reset_attendance(self, request, queryset):
	for rep in queryset.all():
	    rep.is_present = False
	    rep.save()
 
    def export_selected_objects(self, request, queryset):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="reps.csv"'
	writer = csv.writer(response)
	writer.writerow(['Name', 'Company', 'Alumni', 'Present'])
	for rep in queryset.all():
	   writer.writerow([rep.rep, rep.company, rep.is_alumni, rep.is_present])
	return response

    make_attend.short_description = "Mark this representative as present"
    reset_attendance.short_description = "CAUTION:  Mark all selected representatives as not present"
    export_selected_objects.short_description = "Export selected representatives to CSV"


# Now to actually get them to show up on the CMS front end...
from models import ArmoryTableData
admin.site.register(HomePage, HomePageAdmin)
admin.site.register(AboutPage, AboutPageAdmin)
admin.site.register(AgendaPage, PageAdmin)
admin.site.register(ContactPage, PageAdmin)
admin.site.register(PricingPage, PageAdmin)
admin.site.register(RegistrationPage, RegistrationPageAdmin)
admin.site.register(SponsorUsPage, SponsorUsPageAdmin)
admin.site.register(FAQPage, FAQPageAdmin)
admin.site.register(TipPage, PageAdmin)
admin.site.register(StudentProfile, StudentAdmin)
admin.site.register(CompanyProfile, CompanyAdmin)
admin.site.register(CompanyRep, CompanyRepAdmin)
admin.site.register(PayPalInfo)
admin.site.register(SponsorshipPackage)
admin.site.register(ArmoryTableData)
admin.site.register(SponsorshipItem)
