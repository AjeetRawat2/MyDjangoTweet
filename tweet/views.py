from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CommentForm, TweetForm, UserRegistrationForm
from .models import Comment, Follow, Like, Tweet


def _safe_return(request):
    return_to = request.META.get('HTTP_REFERER', '')
    if return_to and url_has_allowed_host_and_scheme(
        return_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(return_to)
    return redirect('tweet_list')


def _feed_context(tweets, user):
    tweets = list(
        tweets.select_related('user')
        .annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True),
            author_followers=Count('user__followers', distinct=True),
        )
        .prefetch_related('comments__user')
    )
    tweet_ids = [tweet.pk for tweet in tweets]
    author_ids = {tweet.user_id for tweet in tweets}
    liked_ids = set()
    followed_ids = set()
    if user.is_authenticated and tweet_ids:
        liked_ids = set(Like.objects.filter(user=user, tweet_id__in=tweet_ids).values_list('tweet_id', flat=True))
        followed_ids = set(Follow.objects.filter(follower=user, following_id__in=author_ids).values_list('following_id', flat=True))
    for tweet in tweets:
        tweet.is_liked = tweet.pk in liked_ids
        tweet.is_following_author = tweet.user_id in followed_ids
    return {'tweets': tweets, 'comment_form': CommentForm()}


def index(request):
    return render(request, 'index.html')


def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    return render(request, 'tweet_list.html', _feed_context(tweets, request.user))


@login_required
def tweet_create(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form})


@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save()
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form': form})


@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        tweet.delete()
        return redirect('tweet_list')
    return render(request, 'tweet_confirm_delete.html', {'tweet': tweet})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def search_tweets(request):
    query = request.GET.get('q', '').strip()
    results = Tweet.objects.filter(Q(text__icontains=query) | Q(user__username__icontains=query)).order_by('-created_at') if query else Tweet.objects.none()
    context = {'query': query, 'results': list(_feed_context(results, request.user)['tweets']), 'comment_form': CommentForm()}
    return render(request, 'search_results.html', context)


@login_required
@require_POST
def toggle_like(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    like, created = Like.objects.get_or_create(tweet=tweet, user=request.user)
    if not created:
        like.delete()
    return _safe_return(request)


@login_required
@require_POST
def add_comment(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.tweet = tweet
        comment.user = request.user
        comment.save()
    else:
        messages.error(request, 'Your comment could not be posted. Keep it under 500 characters and try again.')
    return _safe_return(request)


@login_required
@require_POST
def toggle_follow(request, user_id):
    followed_user = get_object_or_404(User, pk=user_id)
    if followed_user.pk == request.user.pk:
        messages.error(request, 'You cannot follow yourself.')
        return _safe_return(request)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=followed_user)
    if not created:
        follow.delete()
    return _safe_return(request)

