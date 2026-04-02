from django.db import models
from django.contrib.auth.models import User,Group
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


# Create your models here.
class Sprint(models.Model):
    name = models.CharField(max_length=100)
    lead_developer = models.ForeignKey(User, related_name='lead_sprints', on_delete=models.PROTECT)
    developers = models.ManyToManyField(User, related_name='developer_sprints')
    start_date = models.DateField()
    end_date = models.DateField()

    
    def __str__(self):
        return self.name

class Bug(models.Model):
    PLATFORM_CHOICES = [
        ('Windows', 'Windows'),
        ('Web', 'Web'),
        ('iOS', 'iOS'),
        # add more as needed
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Fixed', 'Fixed'),
        ('Closed', 'Closed'),
    ]
    title = models.CharField(max_length=100,default='Sample Bug')
    info = models.TextField()
    screenshot = models.ImageField(upload_to='bug_screenshots/', blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='reported_bugs', on_delete=models.CASCADE)
    fixed_by = models.ForeignKey(User, related_name='fixed_bugs', on_delete=models.SET_NULL, null=True, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES,default='Windows')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')

    # Phone number with basic regex validation (10 digits, no letters)
    
    bug_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    sprint = models.ForeignKey(Sprint, null=True, blank=True, on_delete=models.SET_NULL, related_name='bugs')
    time_spent_hours = models.DecimalField(max_digits=7, decimal_places=5, default=0)


    def __str__(self):
        return f"({self.status})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to ensure `id` is generated
        if not self.bug_id:
            self.bug_id = f'BUG{self.id:03d}'
            super().save(update_fields=['bug_id'])  # Update only `bug_id`

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone_regex = RegexValidator(
        regex=r'^\+?\d{10,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    contact_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        permissions = [('edit_user_profile_perm','EDIT USER PROFILE')]


    

