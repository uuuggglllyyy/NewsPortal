from django.shortcuts import render
from django.core.paginator import Paginator

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