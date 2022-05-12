from django.shortcuts import (
    render, get_object_or_404, get_list_or_404, redirect
)
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from core.utils.paginate_page import paginator_page
from django.views.decorators.cache import cache_page


@cache_page(20, key_prefix="index_page")
def index(request):
    """Представление главной страницы."""
    post_list = get_list_or_404(Post)
    page_obj = paginator_page(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Представление страницы группы."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_page(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Представление страницы профиля."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator_page(posts, request)
    user = request.user
    followers = Follow.objects.filter(author=author)
    if user.is_authenticated:
        following = Follow.objects.filter(
            user=user, author=author
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
        'followers': followers
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Представление страницы информации о посте."""
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, posts=post_id)
    comment = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'author': author,
        'comment': comment,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Представление формы создания поста."""
    template = 'posts/create.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('posts:profile', username=request.user.username)
        return render(request, template, {'form': form})
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Представление формы редактирования поста."""
    template = 'posts/create.html'
    required_post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if required_post.author == request.user:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=required_post
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        context = {
            'form': form,
            'is_edit': is_edit,
            'post_id': post_id
        }
        return render(request, template, context)
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_page(posts, request)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author:
        if not is_follower.exists():
            Follow.objects.create(
                author=author,
                user=user
            )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    followed = Follow.objects.filter(user=user, author=author)
    if followed.exists():
        if user != author:
            followed.delete()
    return redirect('posts:profile', username=username)
