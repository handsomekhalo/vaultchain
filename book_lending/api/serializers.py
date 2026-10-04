from rest_framework import serializers

from book_lending.models import Book

class CreateBooksSerializer(serializers.ModelSerializer):
    """Seriazlier to create books"""
    class Meta:
        model = Book
        fields=[
            'title',"author",'isbn_number','copies_available'
        ]
    

class GetAllBooks(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

        # fields=[
        #     'title',"author",'isbn_number','copies_available'
        # ]
        # read_only_fields = fields


class UpdateBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields=[
            'title',"author",'isbn_number','copies_available'
        ]





    #  title = models.CharField(max_length=100)
    # author= models.CharField(max_length=100)
    # isbn_number =models.CharField(max_length=50, blank=True)
    # copies_available = models.IntegerField(default=0)