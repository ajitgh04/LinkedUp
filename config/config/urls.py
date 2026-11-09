"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from accounts import views as account_views
from connections import views as connection_views
from jobs import views as job_views
from messaging import views as messaging_views
from notifications import views as notification_views
from posts import views as post_views
from profiles import views as profile_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", post_views.feed, name="feed"),
    path("accounts/", include("accounts.urls")),
    path("login/", account_views.login_view, name="login"),
    path("logout/", account_views.logout_view, name="logout"),
    path("profile/", profile_views.my_profile, name="my-profile"),
    path("people/<int:user_id>/", profile_views.profile_detail, name="profile"),
    path("connections/", connection_views.connections, name="connections"),
    path("connections/<int:user_id>/<str:action>/", connection_views.connection_action, name="connection-action"),
    path("posts/<int:post_id>/like/", post_views.toggle_like, name="toggle-like"),
    path("posts/<int:post_id>/comment/", post_views.add_comment, name="add-comment"),
    path("jobs/", job_views.job_list, name="jobs"),
    path("jobs/create/", job_views.create_job, name="create-job"),
    path("jobs/<int:job_id>/apply/", job_views.apply_to_job, name="apply-job"),
    path("messages/", messaging_views.inbox, name="inbox"),
    path("messages/<int:user_id>/", messaging_views.conversation, name="conversation"),
    path("notifications/", notification_views.notification_list, name="notifications"),
    path("search/", profile_views.search, name="search"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
