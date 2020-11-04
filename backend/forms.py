from django import forms


class ProjectForm(forms.Form):
    # id = forms.IntegerField
    name = forms.CharField(max_length=32)
    remark = forms.CharField(max_length=255)
