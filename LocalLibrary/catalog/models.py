from django.db import models
from django.urls import reverse
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from datetime import date
from django.conf import settings
import uuid

# Create your models here.

class Genre(models.Model): 
    """Model representing a book genre"""
    name = models.CharField(max_length=200, unique = True, help_text="Enter a book genre")

    def __str__(self): # String for representing the Model object
        return self.name

    def get_absolute_url(self): # Returns the url to access a particular genre instance
        return reverse('genre-detail', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message = "Genre already exists (case insensitive match)"
            ),
        ]

class Book(models.Model): 
    """Model representing a book (not specific)"""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)
    # Foreign Key used because a book can only have one author but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in file

    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')

    # Use the ManyToManyField because a genre can contain multiple books, and books can cover many genres
    # Genre class has already been defined so we can specify the object above
    genre = models.ManyToManyField(
        Genre, help_text="Select a genre for this book")
    
    language = models.ForeignKey(
        'Language', on_delete=models.SET_NULL, null=True)
    
    def display_genre(self):
        """Creates a string for the Genre"""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def __str__(self): # String for representing the Model object
        return self.title

    def get_absolute_url(self): # Returns the URL to access a detail record for this book
        return reverse('book-detail', args=[str(self.id)])
    
class BookInstance(models.Model):
    """Model representing a specific copy of a book"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date"""
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Book availability')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('bookinstance-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'
    
class Author(models.Model):
    """Model representing an author"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True,blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', "first_name"]

    def get_absolute_url(self):
        """Returns the URL to access an author instance"""
        return reverse('author-detail', args=[str(self.id)])
    
    def __str__(self):
        """String for representing the Model object"""
        return f'{self.last_name}, {self.first_name}'

class Language(models.Model):
    """Model representing a language"""
    name = models.CharField(max_length=50)  # Language name (e.g., Farsi)

    def get_absolute_url(self):
        """Returns the url to access a language instance"""
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object"""
        return self.name
