import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


ROOMS = (
    ('first-sip', 'First Sip', 'Introductions, little life updates, and easy hellos.', '☕'),
    ('little-joys', 'Little Joys', 'Share the small things that make an ordinary day better.', '🌼'),
    ('chai-and-chuckles', 'Chai & Chuckles', 'Funny stories, silly questions, and low-stakes fun.', '😄'),
    ('screens-and-songs', 'Screens & Songs', 'Talk about what you are watching or listening to.', '🎬'),
    ('open-table', 'The Open Table', 'A relaxed place for any kind conversation.', '🫖'),
)


def seed_rooms(apps, schema_editor):
    ChaiRoom = apps.get_model('tweet', 'ChaiRoom')
    for slug, name, description, emoji in ROOMS:
        ChaiRoom.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'description': description, 'emoji': emoji},
        )


def remove_seeded_rooms(apps, schema_editor):
    ChaiRoom = apps.get_model('tweet', 'ChaiRoom')
    ChaiRoom.objects.filter(slug__in=[room[0] for room in ROOMS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tweet', '0002_social_features'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChaiRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('slug', models.SlugField(max_length=90, unique=True)),
                ('emoji', models.CharField(default='☕', max_length=8)),
                ('description', models.CharField(max_length=180)),
            ],
            options={'ordering': ('name',)},
        ),
        migrations.CreateModel(
            name='ChaiMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.CharField(max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='tweet.chairoom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chai_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('created_at', 'pk')},
        ),
        migrations.AddIndex(
            model_name='chaimessage',
            index=models.Index(fields=['room', 'created_at'], name='chai_msg_room_time_idx'),
        ),
        migrations.RunPython(seed_rooms, remove_seeded_rooms),
    ]
