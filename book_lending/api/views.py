from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
import json
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from book_lending.api.serializers import CreateBooksSerializer, GetAllBooks, UpdateBookSerializer
from book_lending.models import Book


@api_view(['POST'])
@permission_classes([AllowAny])
def create_book_library_api(request):
    "create list of books to be aaded to list of available books"
    data = request.data

    serializer = CreateBooksSerializer(data =request.data)


    if not serializer.is_valid():
        print('invalid')
        return Response({'error': 'Please provide all details  of book'},
                         status=status.HTTP_400_BAD_REQUEST)
    
    if serializer.is_valid():
        book=serializer.save(
            title =data.get('title'),
            author =data.get('author'),
            isbn_number=data.get('isbn_number'),
            copies_available =data.get('copies_available')
        )

        return Response({
            "message": "Case created successfully.",
            "id":book.id,
            "title":book.title,
            "author":book.author,
            "isbn_number":book.isbn_number,
            "copies_available":book.copies_available,
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
    

    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_books_api(request):

    if request.method == "GET":
        books = Book.objects.all()

        serializer = GetAllBooks(books, many=True).data
    
        print('serializer',serializer)

        return Response({
            'status': 'success',
            'data':serializer
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_book_details(request, book_id):
    book = get_object_or_404(
        Book, pk=book_id
    )

    serializer = UpdateBookSerializer(book, 
                                      data=request.data,partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({'Message', 'Updated Succesfully'})
    
    return Response(serializer.errors, status=400)




