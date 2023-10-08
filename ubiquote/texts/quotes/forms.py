from django import forms
from .models import Quote


class QuoteForm(forms.ModelForm):
    
    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        if categories.count() > 3:
            raise forms.ValidationError('You can associate a maximum of 3 categories.')
        return categories    
    
    class Meta:
        model = Quote
        fields = ('text', 'author', 'lang', 'categories') # 'contributor'
        widgets = {
            'text': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : "Put your quote here"}),
            'author': forms.Select(attrs={'class' : 'form-control'}),
            # 'contributor': forms.Select(attrs={'class' : 'form-control'}),
            'lang': forms.Select(attrs={'class' : 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class' : 'form-control'}),
        }

