from django import forms
from .models import Favorite


class FormFavorite(forms.ModelForm):
    class Meta:
        model = Favorite

        fields = ['title', 'rating', 'author']

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')

        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating should be between 1 to 5")

        return rating
