from django.urls import path

from ia import views

app_name = "ia"

urlpatterns = [
    path("api/chat/", views.chat, name="chat"),
    path("api/chat/stream/", views.chat_stream, name="chat_stream"),
]
