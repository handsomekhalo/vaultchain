from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=100)
    author= models.CharField(max_length=100)
    isbn_number =models.CharField(max_length=50, blank=True)
    copies_available = models.IntegerField(default=0)

class Loan(models.Model):
    title_of_book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower_name = models.CharField(max_length=100)
    borrowed_at=models.DateTimeField(null=True, blank=True)
    returned_at =models.DateTimeField(null=True, blank=True)



    