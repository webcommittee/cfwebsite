from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from django.shortcuts import redirect
import views

urlpatterns =  i18n_patterns(
    url(r'^company-registration/$', views.company_register, name='company-register'), 
    url(r'^student-registration/$', views.student_register, name='student-register'), 
    url(r'^company-slug/(?P<uid>[0-9]+).html/$', views.company_redirect, name='company-slug'),
    url(r'^student-slug/(?P<uid>[0-9]+).html/$', views.student_redirect, name='student-slug'),
    url(r'^dashboard/edit_profile/$', views.edit_profile, name="edit_profile"),
    url(r'^company-search/$', views.company_search, name='company-search'),
    url(r'^student-search/$', views.student_search, name='student-search'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^return_paypal/$', views.return_me, name='return_paypal'),
    url(r'^dashboard/prepaymentscreen/$', views.view_that_asks_for_money, name="buy"),
    url(r'^paypal-ipn/', include('paypal.standard.ipn.urls')),
    url(r'^success/$', views.pay_success),
    url(r'^bookings/get/(?P<day>[a-z]+)/$', views.get_bookings, name='dashboard/prepaymentscreen/bookings/get/100'),
    url(r'^bookings/post_all/(?P<day>[a-z]+)/$', views.book_all_tables, name='book all'),
    url(r'^bookings/get_company/(?P<uid>[0-9]+)/(?P<day>[a-z]+)/$', views.get_company_booking, name='dashboard/prepaymentscreen/bookings/get/100'),
    url(r'^bookings/post/$', views.book_table, name='dashboard/prepaymentscreen/bookings/post/100'),
    url(r'^companies/armory-layout/$' , views.armory_manipulation),
    url(r'^user/password/reset/$', 
        password_reset, 
        {'post_reset_redirect' : '/user/password/reset/done/'},
        name="password_reset"),
    url(r'^user/password/reset/done/$',
        password_reset_done,
        name="password_reset_done"),
    url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
        password_reset_confirm, 
        {'post_reset_redirect' : '/user/password/done/'},
        name='password_reset_confirm'),
    url(r'^user/password/done/$', 
        password_reset_complete,
        {'post_reset_redirect' : '/'},
        name="password_reset_complete",),
)
