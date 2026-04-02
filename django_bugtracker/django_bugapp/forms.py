from django import forms
from .models import Bug ,UserProfile,Sprint
from django.contrib.auth.models import User,Group
from django.contrib.auth.forms import UserCreationForm
class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['status','title','info','screenshot','platform','sprint']

class BugStatusUploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.xlsx'):
            raise forms.ValidationError("Only .xlsx files are allowed.")
        return file

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['contact_number','bio']

class CustomRegisterForm(UserCreationForm):
    
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Role",
        empty_label="Select a role",
        widget=forms.Select(attrs={"class": "form-control w-full border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"})
    )
    class Meta:
        model = User
        fields = ['username','email','password1','password2','role']

class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = '__all__'
        widgets = {
            'developers': forms.CheckboxSelectMultiple(),  
        }

    
    def __init__(self, *args, **kwargs):
        lead_developer = kwargs.get('instance', None).lead_developer if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)

        developer_group = Group.objects.get(name='Developer')
        dev_qs = User.objects.filter(groups=developer_group)
        
        # Exclude lead developer if set
        if lead_developer:
            dev_qs = dev_qs.exclude(id=lead_developer.id)
        
        self.fields['developers'].queryset = dev_qs
        self.fields['lead_developer'].queryset = User.objects.all()
    
    
    def clean(self):
        cleaned_data = super().clean()
        lead = cleaned_data.get('lead_developer')
        developers = cleaned_data.get('developers')
        if lead and developers and lead in developers:
            raise forms.ValidationError("Lead developer cannot be listed as a developer.")
        return cleaned_data