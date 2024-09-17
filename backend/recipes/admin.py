from django.contrib import admin


from .models import Ingredient, Tag, Recipe, Favorite, RecipeIngredient

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    search_fields =[
        'author',
        'name',
    ]
    list_filter = [
        'tags',
    ]
    fieldsets = (
        (None, {'fields': ('name', 'author', 'favorite_count', 'tags')}),
        ('Описание', {'fields': ('text', 'cooking_time', 'created_at')})
    )
    inlines = [RecipeIngredientInline]


    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorite_count.short_descriptrion = 'В избранном'

@admin.register(Ingredient)
class  IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = [
        'name',
    ]