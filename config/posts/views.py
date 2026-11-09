from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import Notification

from .models import Comment, Like, Post


@login_required
def feed(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if not content:
            messages.error(request, "Add a few words before sharing your post.")
        else:
            post = Post.objects.create(
                author=request.user,
                content=content,
                image=request.FILES.get("image"),
            )
            messages.success(request, "Your post is live.")
            return redirect("feed")
    posts = Post.objects.select_related("author").annotate(
        like_count=Count("likes", distinct=True),
        comment_count=Count("comments", distinct=True),
        viewer_liked=Exists(
            Like.objects.filter(post_id=OuterRef("pk"), user=request.user)
        ),
    ).prefetch_related("comments__user")[:30]
    return render(request, "posts/feed.html", {"posts": posts})


@login_required
def toggle_like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=post_id)
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
        elif post.author_id != request.user.pk:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                kind="like",
                message=f"{request.user.get_full_name() or request.user.username} liked your post.",
                url="/",
            )
    return redirect("feed")


@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=post_id)
        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
            if post.author_id != request.user.pk:
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    kind="comment",
                    message=f"{request.user.get_full_name() or request.user.username} commented on your post.",
                    url="/",
                )
        else:
            messages.error(request, "Write a comment before posting it.")
    return redirect("feed")
