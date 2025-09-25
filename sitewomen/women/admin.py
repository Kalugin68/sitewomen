from django.contrib import admin, messages   # админка и сообщения
from django.utils.safestring import mark_safe

from .models import Women, Category          # импортируем модели


# Кастомный фильтр для статуса женщины (замужем/не замужем)
class MarriedFilter(admin.SimpleListFilter):
    title = "Статус женщин"          # заголовок фильтра
    parameter_name = "status"        # имя параметра в URL

    def lookups(self, request, model_admin):
        # варианты для фильтра
        return [
            ('married', 'Замужем'),
            ('single', 'Не замужем'),
        ]

    def queryset(self, request, queryset):
        # фильтрация по мужу
        if self.value() == 'married':
            return queryset.filter(husband__isnull=False)
        elif self.value() == 'single':
            return queryset.filter(husband__isnull=True)


# Настройка админки для Women
@admin.register(Women)
class WomenAdmin(admin.ModelAdmin):
    fields = ['title', 'slug', 'content', 'photo', 'post_photo', 'cat', 'husband', 'tags']  # поля формы
    # exclude = ['tags', 'is_published']
    readonly_fields = ['post_photo']
    prepopulated_fields = {'slug': ('title',)}  # автогенерация slug
    # filter_horizontal = ('tags',)
    filter_vertical = ['tags']                  # выбор тегов вертикально
    list_display = ('title', 'post_photo', 'time_create', 'is_published', 'cat')  # колонки списка
    list_display_links = ('title',)             # кликабельные поля
    ordering = ['-time_create', 'title']        # сортировка по умолчанию
    list_editable = ("is_published", )          # быстрое редактирование
    list_per_page = 5                           # пагинация
    actions = ['set_published', 'set_draft']    # действия
    search_fields = ['title__startswith', 'cat__name']  # поиск
    list_filter = [MarriedFilter, 'cat__name', 'is_published']  # фильтры
    save_on_top = True

    @admin.display(description="Изображение", ordering="content")
    def post_photo(self, women: Women):
        if women.photo:
            return mark_safe(f"<img src='{women.photo.url}' width=50>")
        else:
            return "Без фото"

    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        # массовая публикация
        count = queryset.update(is_published=Women.Status.PUBLISHED)
        self.message_user(request, f"Изменено {count} записей.")

    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        # массовое снятие публикации
        count = queryset.update(is_published=Women.Status.DRAFT)
        self.message_user(request, f"{count} записей снято с публикации!", messages.WARNING)


# Настройка админки для Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')          # колонки
    list_display_links = ('id', 'name')    # кликабельные колонки

# admin.site.register(Women, WomenAdmin)  # альтернативная регистрация
