from collections import Counter
import re

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Max, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import CommentForm, TweetForm, UserRegistrationForm
from .models import ChaiMessage, ChaiRoom, Comment, Follow, Like, Tweet


def _safe_return(request):
    return_to = request.META.get('HTTP_REFERER', '')
    if return_to and url_has_allowed_host_and_scheme(
        return_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(return_to)
    return redirect('tweet_list')


def csrf_failure(request, reason=''):
    # A login page restored from Android/Chrome's back-forward cache can contain
    # a token from before the browser's CSRF cookie rotated. Refresh the form.
    auth_form_views = {
        '/accounts/login': 'login',
        '/register': 'register',
    }
    form_view = auth_form_views.get(request.path.rstrip('/'))
    if (
        request.method == 'POST'
        and form_view
        and reason.startswith('CSRF token from POST incorrect')
    ):
        response = redirect(f'{reverse(form_view)}?csrf=refresh')
        response['Cache-Control'] = 'no-store'
        return response

    return HttpResponse(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Refresh your page · Chai &amp; Chatter</title>'
        '<body style="font:16px system-ui;max-width:34rem;margin:12vh auto;padding:1.5rem;color:#172033">'
        '<h1>Let’s refresh that page</h1>'
        '<p>For your security, this request could not be verified. Reload the page and try again.</p>'
        '<p><a href="/">Back to Chai &amp; Chatter</a></p></body></html>',
        status=403,
        content_type='text/html; charset=utf-8',
    )


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
        # Render can lose local uploads between deploys; do not let missing
        # media files break the entire feed when templates inspect dimensions.
        tweet.photo_available = bool(
            tweet.photo and tweet.photo.storage.exists(tweet.photo.name)
        )
        tweet.is_liked = tweet.pk in liked_ids
        tweet.is_following_author = tweet.user_id in followed_ids
    return {'tweets': tweets, 'comment_form': CommentForm()}


CHAI_QUESTIONS = (
    'What small thing made you smile this week?',
    'What is your perfect chai-and-snack combination?',
    'If you could take a chai break anywhere, where would you go?',
    'What song always makes a regular day better?',
    'What is a tiny joy you wish more people noticed?',
    'Which movie can you happily watch again and again?',
    'What is the best advice a friend has given you?',
    'If today had a theme song, what would it be?',
    'What is one place in your town everyone should visit?',
    'What is your funniest harmless chai-time story?',
    'What new hobby would you try with a friend?',
    'What does a really good weekend look like to you?',
)


def _daily_chai_question():
    day_number = timezone.localdate().toordinal()
    return CHAI_QUESTIONS[day_number % len(CHAI_QUESTIONS)]


def chai_tables(request):
    rooms = ChaiRoom.objects.annotate(
        message_count=Count('messages'),
        people_count=Count('messages__user', distinct=True),
        latest_activity=Max('messages__created_at'),
    )
    return render(request, 'chai_tables.html', {
        'rooms': rooms,
        'chai_question': _daily_chai_question(),
    })


@login_required
def chai_table(request, slug):
    room = get_object_or_404(ChaiRoom, slug=slug)
    chat_messages = list(room.messages.select_related('user').order_by('-pk')[:60])
    chat_messages.reverse()
    return render(request, 'chai_room.html', {
        'room': room,
        'chat_messages': chat_messages,
        'latest_message_id': chat_messages[-1].pk if chat_messages else 0,
        'chai_question': _daily_chai_question(),
    })


def _chai_message_payload(message):
    return {
        'id': message.pk,
        'username': message.user.username,
        'user_id': message.user_id,
        'body': message.body,
        'created_at': timezone.localtime(message.created_at).isoformat(),
    }


@login_required
@require_http_methods(['GET', 'POST'])
def chai_room_messages(request, slug):
    room = get_object_or_404(ChaiRoom, slug=slug)
    if request.method == 'GET':
        try:
            after_id = max(0, int(request.GET.get('after', '0')))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid message cursor.'}, status=400)
        messages = room.messages.filter(pk__gt=after_id).select_related('user').order_by('pk')[:60]
        response = JsonResponse({'messages': [_chai_message_payload(message) for message in messages]})
        response['Cache-Control'] = 'no-store'
        return response

    body = request.POST.get('body', '').strip()
    if not body:
        return JsonResponse({'error': 'Write a message before sending.'}, status=400)
    if len(body) > 300:
        return JsonResponse({'error': 'Keep your message under 300 characters.'}, status=400)
    message = ChaiMessage.objects.create(room=room, user=request.user, body=body)
    return JsonResponse({'message': _chai_message_payload(message)}, status=201)


@require_GET
def service_worker(request):
    response = HttpResponse(
        "importScripts('/static/tweet/js/service-worker.js');",
        content_type='application/javascript',
    )
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response


def index(request):
    return render(request, 'index.html')


def _trending_topics():
    counts = Counter()
    recent_texts = Tweet.objects.order_by('-created_at').values_list('text', flat=True)[:250]
    for text in recent_texts:
        counts.update(tag.casefold() for tag in re.findall(r'(?<!\w)#([\w]+)', text))
    return [{'tag': tag, 'posts': count} for tag, count in counts.most_common(4)]


def tweet_list(request):
    feed_mode = 'following' if request.GET.get('feed') == 'following' else 'for-you'
    tweets = Tweet.objects.all().order_by('-created_at')
    if feed_mode == 'following':
        if request.user.is_authenticated:
            tweets = tweets.filter(user__followers__follower=request.user)
        else:
            tweets = tweets.none()

    feed_context = _feed_context(tweets, request.user)
    suggested_users = User.objects.all()
    if request.user.is_authenticated:
        suggested_users = suggested_users.exclude(pk=request.user.pk)
        followed_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        suggested_users = suggested_users.exclude(pk__in=followed_ids)
    suggested_users = suggested_users.annotate(follower_count=Count('followers')).order_by('-follower_count', 'username')[:3]
    feed_context.update({
        'feed_mode': feed_mode,
        'suggested_users': suggested_users,
        'trending_topics': _trending_topics(),
        'chai_question': _daily_chai_question(),
    })
    return render(request, 'tweet_list.html', feed_context)

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


@never_cache
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
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'is_liked': created, 'like_count': tweet.likes.count()})
    response = _safe_return(request)
    response['Location'] = f"{response['Location'].split('#', 1)[0]}#tweet-{tweet.pk}"
    return response


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
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'comment': {
                    'id': comment.pk,
                    'username': comment.user.username,
                    'body': comment.text,
                    'created_at': timezone.localtime(comment.created_at).isoformat(),
                    'comment_count': tweet.comments.count(),
                },
            }, status=201)
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Your comment could not be posted. Keep it under 500 characters and try again.'}, status=400)
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

