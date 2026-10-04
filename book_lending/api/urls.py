from django.urls import path
from .views import create_book_library_api, get_all_books_api, update_book_details


urlpatterns=[
    path('create_book_library_api/', create_book_library_api, name='create_book_library_api'),
    path('get_all_books_api/', get_all_books_api,name='get_all_books_api' ),
    path('update_book_details/<int:book_id>/', update_book_details, name='update_book_details')
    # path('update_case_api/<int:case_id>/', views.update_case_api, name="update_case_api"),

]