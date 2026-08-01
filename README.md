# 🐦 MyDjangoTweet

<p align="center">
  <img src="https://img.shields.io/badge/Django-Web%20Framework-092E20?logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Authentication-Django-success" alt="Authentication">
  <img src="https://img.shields.io/badge/Deployed%20on-Render-000000?logo=render&logoColor=white" alt="Render">
</p>

<p align="center">
  A lightweight social media application built with <b>Django</b> where users can create, edit, delete, search, and share tweets with optional images.
</p>

<p align="center">
  <a href="https://mydjangotweet.onrender.com/">
    🌐 Live Demo
  </a>
  &nbsp;•&nbsp;
  <a href="https://github.com/AjeetRawat2/MyDjangoTweet">
    💻 Source Code
  </a>
</p>

---

## 📖 About

**MyDjangoTweet** is a Twitter-inspired social media web application built using **Python and Django**.

Users can create an account, log in, publish short posts, attach images, edit their own tweets, delete them, browse recent posts, and search tweets by content or username.

The project demonstrates core Django concepts including:

* Django Models
* Forms
* Authentication
* CRUD operations
* File uploads
* Database relationships
* Query filtering
* Template rendering
* Protected routes

---

## ✨ Features

### 🔐 User Authentication

Users can register for an account and log in to access protected functionality.

After successful registration, the application automatically logs the new user in.

---

### 📝 Create Tweets

Authenticated users can create tweets containing up to:

```text
240 characters
```

Each tweet is automatically connected to the currently logged-in user.

---

### 🖼️ Image Uploads

Tweets can optionally include an image.

```python
photo = models.ImageField(
    upload_to='photos/',
    blank=True,
    null=True
)
```

This means users can publish either:

```text
📝 Text only

or

📝 Text + 🖼️ Image
```

---

### ✏️ Edit Tweets

Users can edit tweets they created.

Tweet ownership is checked before editing:

```python
tweet = get_object_or_404(
    Tweet,
    pk=tweet_id,
    user=request.user
)
```

This prevents one user from editing another user's tweet.

---

### 🗑️ Delete Tweets

Users can also delete their own tweets.

Delete operations are protected with:

```python
@login_required
```

and ownership verification.

---

### 🔎 Search Tweets

MyDjangoTweet includes search functionality that searches both:

* Tweet content
* Username

The application uses Django `Q` objects:

```python
Tweet.objects.filter(
    Q(text__icontains=query) |
    Q(user__username__icontains=query)
)
```

This provides case-insensitive searching.

---

### 🕐 Latest Tweets First

Tweets are displayed with the newest posts first:

```python
Tweet.objects.all().order_by('-created_at')
```

---

## 🛠️ Tech Stack

| Technology     | Purpose             |
| -------------- | ------------------- |
| 🐍 Python      | Backend programming |
| 🌿 Django      | Web framework       |
| 🗄️ Django ORM | Database operations |
| 🎨 HTML / CSS  | Frontend interface  |
| 🔐 Django Auth | Authentication      |
| 🖼️ ImageField | Tweet image uploads |
| ☁️ Render      | Deployment          |

---

# 🏗️ Application Architecture

```text
                👤 User
                  │
                  ▼
          ┌───────────────┐
          │ Django Views  │
          └───────┬───────┘
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
     Create      Search    Edit/Delete
      Tweet      Tweets      Tweet
        │         │          │
        └─────────┼──────────┘
                  ▼
           ┌─────────────┐
           │ Django ORM  │
           └──────┬──────┘
                  ▼
           ┌─────────────┐
           │  Database   │
           └──────┬──────┘
                  ▼
           ┌─────────────┐
           │  Templates  │
           └──────┬──────┘
                  ▼
              🌐 Browser
```

---

# 📊 Tweet Model

The core database model is:

```python
class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    text = models.TextField(
        max_length=240
    )

    photo = models.ImageField(
        upload_to='photos/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
```

Each tweet contains:

| Field        | Description                           |
| ------------ | ------------------------------------- |
| `user`       | User who created the tweet            |
| `text`       | Tweet content, maximum 240 characters |
| `photo`      | Optional uploaded image               |
| `created_at` | Tweet creation time                   |
| `updated_at` | Last modification time                |

---

# 🔄 Tweet Lifecycle

```text
👤 User Login
      ↓
📝 Create Tweet
      ↓
Enter text (max 240 characters)
      ↓
Optional image upload
      ↓
💾 Save Tweet
      ↓
Django ORM
      ↓
🗄️ Database
      ↓
🐦 Tweet Feed
```

The tweet can later be:

```text
              🐦 Tweet
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
      View      Edit      Delete
                 │          │
                 └────┬─────┘
                      ▼
               Ownership Check
                      │
                      ▼
                Update Database
```

---

# 🔐 Authentication & Authorization

Several operations require authentication:

```python
@login_required
def tweet_create(request):
```

```python
@login_required
def tweet_edit(request, tweet_id):
```

```python
@login_required
def tweet_delete(request, tweet_id):
```

Additionally, editing and deleting verify ownership using:

```python
user=request.user
```

So a user cannot modify another user's tweet through these views.

---

# 📂 Suggested Project Structure

```text
MyDjangoTweet/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── tweet/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── templates/
│   ├── index.html
│   ├── tweet_list.html
│   ├── tweet_form.html
│   ├── tweet_confirm_delete.html
│   ├── search_results.html
│   │
│   └── registration/
│       ├── login.html
│       └── register.html
│
└── media/
    └── photos/
```

> The exact folder names may differ depending on your current Django project structure.

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/AjeetRawat2/MyDjangoTweet.git
```

Enter the project:

```bash
cd MyDjangoTweet
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

If the repository contains `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 5. Start the Development Server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

---

# 🎮 How to Use

### 1️⃣ Register

Create a new account through the registration page.

After successful registration, the application automatically logs you in.

### 2️⃣ Create a Tweet

Write your tweet with up to **240 characters** and optionally upload an image.

### 3️⃣ Browse Tweets

Open the tweet feed to see posts ordered from newest to oldest.

### 4️⃣ Search

Search using:

```text
Tweet text
      OR
Username
```

### 5️⃣ Manage Your Tweets

When logged in, you can edit or delete tweets belonging to your account.

---

# 🌐 Live Deployment

The project is deployed on **Render**.

### 🚀 Live Website

https://mydjangotweet.onrender.com/

---

# 🗺️ Current Feature Flow

```text
                 MyDjangoTweet 🐦
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
   🔐 Authentication              🐦 Tweets
        │                             │
   ┌────┴────┐             ┌─────────┼─────────┐
   ▼         ▼             ▼         ▼         ▼
Register    Login        Create     Edit      Delete
                           │
                           ▼
                     Text + Image

                       🔎 Search
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                Tweet Text   Username
```

---

# 🔮 Future Improvements

Some possible upgrades for the project:

* ❤️ Like system
* 💬 Comments and replies
* 👥 Follow / unfollow users
* 👤 User profile pages
* 🖼️ Profile pictures
* 🔁 Retweets
* 🔖 Bookmark tweets
* 🔔 Notifications
* #️⃣ Hashtag support
* 🌙 Dark mode
* 📱 Improved mobile interface
* ♾️ Infinite scrolling
* 🔗 Shareable tweet URLs
* REST API using Django REST Framework

---

# 🎯 Learning Outcomes

This project demonstrates practical experience with:

* Django project architecture
* Models and database relationships
* Django ORM
* Authentication and authorization
* CRUD operations
* Form handling
* File uploads
* Query filtering with `Q`
* Django templates
* Login-protected routes
* Deploying a Django web application

---

## 👨‍💻 Author

**Ajeet Rawat**

GitHub: [@AjeetRawat2](https://github.com/AjeetRawat2)

Repository: [MyDjangoTweet](https://github.com/AjeetRawat2/MyDjangoTweet)

---

## ⭐ Support

If you like **MyDjangoTweet**, consider giving the repository a ⭐.

<p align="center">
  🐦 Built with Python & Django
</p>
