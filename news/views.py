from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Author
from .forms import PostForm, NewsSearchForm  # Создадим PostForm ниже
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class PostList(ListView):
    model = Post
    ordering = '-date_created'
    template_name = 'news/post_list.html'  # Убедитесь, что этот шаблон существует
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.post_type = self.request.GET.get('post_type', 'NW')  # NW как default
        if self.post_type not in ['NW', 'AR']:
            self.post_type = 'NW'  # Validation
        queryset = queryset.filter(post_type=self.post_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = self.post_type
        context['is_news'] = self.post_type == 'NW'
        context['is_article'] = self.post_type == 'AR'
        return context

class PostDetail(DetailView):
    model = Post
    template_name = 'news/post_detail.html'  # Убедитесь, что этот шаблон существует
    context_object_name = 'post'

class BasePostCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/post_edit.html'  # Убедитесь, что этот шаблон существует
    # success_url = reverse_lazy('post_list')  #  Удаляем, т.к. переопределяем метод

    def form_valid(self, form):
        post = form.save(commit=False)
        # Получаем текущего авторизованного пользователя и связываем его с автором
        author = Author.objects.get(user=self.request.user)  # Get Author instance
        post.author = author
        post.post_type = self.post_type
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('news_list')  # Перенаправляем на news_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type_name'] = 'Новость' if self.post_type == 'NW' else 'Статья'
        return context


class NewsCreate(BasePostCreate):
    post_type = 'NW'  # Новости


class ArticleCreate(BasePostCreate):
    post_type = 'AR'  # Статьи


class BasePostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.add_post',)
    model = Post
    form_class = PostForm
    template_name = 'news/post_edit.html'  # Убедитесь, что этот шаблон существует

    def get_success_url(self):
        return reverse('news_list')  # Перенаправляем на news_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post_type_name'] = 'Новость' if post.post_type == 'NW' else 'Статья'
        return context


class NewsUpdate(LoginRequiredMixin, BasePostUpdate):
    pass


class ArticleUpdate(LoginRequiredMixin, BasePostUpdate):
    pass


class BasePostDelete(DeleteView):
    model = Post
    template_name = 'news/post_delete.html'  # Убедитесь, что этот шаблон существует

    # success_url = reverse_lazy('post_list') #  Удаляем, т.к. переопределяем метод

    def get_success_url(self):
        return reverse('news_list')  # Перенаправляем на news_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post_type_name'] = 'Новость' if post.post_type == 'NW' else 'Статья'
        return context


class NewsDelete(BasePostDelete):
    pass


class ArticleDelete(BasePostDelete):
    pass


def news_search(request):
    form = NewsSearchForm(request.GET)  # Заполняем форму данными из GET-запроса
    news = Post.objects.all()  # Получаем все новости (изначально)

    if form.is_valid():
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        date_after = form.cleaned_data.get('date_after')

        # Фильтрация
        if title:
            news = news.filter(title__icontains=title)  # Поиск по названию

        if author:
            news = news.filter(
                author__user__username__icontains=author)  # Поиск по автору (предполагается поле author в модели)

        if date_after:
            news = news.filter(date_created__gte=date_after)  # Дата позже указанной

    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'news/news_search.html', context)


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




