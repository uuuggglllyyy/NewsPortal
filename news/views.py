from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post
from .forms import NewsSearchForm
from django.db.models import Q # Import Q object

from .models import Post

def news_list(request):
    news = Post.objects.all().order_by('-date_created')  # Сортируем по дате в убывающем порядке
    total_news = news.count()  # Получаем общее количество новостей

    # Пагинация
    paginator = Paginator(news, 10)  # 10 новостей на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Получаем нужную страницу

    context = {
        'page_obj': page_obj,  # Передаём объект страницы
        'total_news': total_news,
    }

    return render(request, 'news/news_list.html', context)

def news_detail(request, news_id):
    news = Post.objects.get(id=news_id)
    return render(request, 'news/news_detail.html', {'news': news})

def news_search(request):
    form = NewsSearchForm(request.GET) # Заполняем форму данными из GET-запроса
    news = Post.objects.all()  # Получаем все новости (изначально)

    if form.is_valid():
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        date_after = form.cleaned_data.get('date_after')

        # Фильтрация
        if title:
            news = news.filter(title__icontains=title) #Поиск по названию

        if author:
            news = news.filter(author__user__username__icontains=author) #Поиск по автору (предполагается поле author в модели)

        if date_after:
            news = news.filter(date_created__gte=date_after) #Дата позже указанной

    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'news/news_search.html', context)