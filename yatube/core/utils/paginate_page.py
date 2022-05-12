from django.core.paginator import Paginator


def paginator_page(post_list, request, posts_per_page=10):
    paginator = Paginator(post_list, posts_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
