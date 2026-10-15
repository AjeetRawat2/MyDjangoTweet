document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('[data-login-form]')) {
    window.addEventListener('pageshow', (event) => {
      if (event.persisted) window.location.reload();
    });
  }

  const revealTargets = document.querySelectorAll('[data-reveal], .post-card');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries, currentObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          currentObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -24px 0px' });
    revealTargets.forEach((element) => observer.observe(element));
  } else {
    revealTargets.forEach((element) => element.classList.add('is-visible'));
  }

  document.querySelectorAll('.feed-list .post-card').forEach((card, index) => {
    card.style.setProperty('--post-order', index);
    card.querySelectorAll('.comment-item').forEach((comment, commentIndex) => {
      comment.style.setProperty('--comment-order', commentIndex);
    });
  });

  document.querySelectorAll('.comment-count[href^="#comments-"]').forEach((trigger) => {
    trigger.addEventListener('click', (event) => {
      const dialog = document.getElementById(trigger.hash.slice(1));
      if (!dialog || typeof dialog.showModal !== 'function') return;
      event.preventDefault();
      dialog.showModal();
    });
  });

  document.querySelectorAll('.comments-dialog').forEach((dialog) => {
    dialog.querySelector('[data-close-comments]')?.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', (event) => {
      if (event.target === dialog) dialog.close();
    });
  });

  document.querySelectorAll('.like-button[type="submit"]').forEach((button) => {
    button.addEventListener('click', () => {
      button.classList.remove('is-animating');
      requestAnimationFrame(() => button.classList.add('is-animating'));
    });
    button.addEventListener('animationend', () => button.classList.remove('is-animating'));
  });

  document.querySelectorAll('.comment-form').forEach((form) => {
    const textarea = form.querySelector('textarea');
    if (!textarea) return;

    const resizeTextarea = () => {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    };
    textarea.addEventListener('input', resizeTextarea);
    resizeTextarea();

    form.addEventListener('submit', () => {
      if (textarea.value.trim()) form.classList.add('is-sending');
    });
  });

  const upload = document.querySelector('input[type="file"]');
  if (upload) {
    upload.addEventListener('change', () => {
      const label = document.querySelector('.file-label');
      const zone = document.querySelector('.upload-zone');
      if (label && upload.files && upload.files.length) {
        label.textContent = upload.files[0].name;
        if (zone) zone.classList.add('has-file');
      }
    });
  }

  const root = document.documentElement;
  const themeButtons = document.querySelectorAll('[data-theme-toggle]');
  const savedTheme = localStorage.getItem('chai-chatter-theme');
  if (savedTheme === 'light' || savedTheme === 'dark') root.dataset.theme = savedTheme;
  const syncThemeButtons = () => {
    const dark = root.dataset.theme === 'dark';
    themeButtons.forEach((button) => {
      button.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
      button.setAttribute('title', dark ? 'Switch to light theme' : 'Switch to dark theme');
      const icon = button.querySelector('.cc-theme-icon');
      if (icon) icon.textContent = dark ? '☀' : '☾';
      const label = button.querySelector('.cc-theme-label');
      if (label) label.textContent = dark ? 'Light theme' : 'Dark theme';
    });
  };
  syncThemeButtons();
  themeButtons.forEach((button) => button.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('chai-chatter-theme', root.dataset.theme);
    syncThemeButtons();
  }));

  document.querySelectorAll('[data-like-form]').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const button = form.querySelector('.like-button');
      if (!button || button.disabled) return;
      const wasLiked = button.classList.contains('is-liked');
      button.disabled = true;
      button.classList.toggle('is-liked', !wasLiked);
      button.setAttribute('aria-pressed', String(!wasLiked));
      button.setAttribute('aria-label', !wasLiked ? 'Unlike post' : 'Like post');
      button.classList.remove('is-animating');
      requestAnimationFrame(() => button.classList.add('is-animating'));
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          credentials: 'same-origin'
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Like could not be saved.');
        button.classList.toggle('is-liked', result.is_liked);
        button.setAttribute('aria-pressed', String(result.is_liked));
        button.setAttribute('aria-label', result.is_liked ? 'Unlike post' : 'Like post');
        button.dataset.likeCount = String(result.like_count);
      } catch (_error) {
        button.classList.toggle('is-liked', wasLiked);
        button.setAttribute('aria-pressed', String(wasLiked));
        button.setAttribute('aria-label', wasLiked ? 'Unlike post' : 'Like post');
      } finally {
        button.disabled = false;
        window.setTimeout(() => button.classList.remove('is-animating'), 600);
      }
    });
  });

  document.querySelectorAll('[data-comment-form]').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const textarea = form.querySelector('textarea');
      const submitButton = form.querySelector('button[type="submit"]');
      const dialog = form.closest('.comments-dialog');
      const thread = dialog?.querySelector('.comments-panel');
      const trigger = dialog ? document.querySelector('.comment-count[href="#' + dialog.id + '"]') : null;
      if (!textarea || !thread || !submitButton || !textarea.value.trim()) return;
      submitButton.disabled = true;
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          credentials: 'same-origin'
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Comment could not be posted.');
        const comment = result.comment;
        const item = document.createElement('div');
        item.className = 'comment-item is-new';
        const avatar = document.createElement('span');
        avatar.className = 'comment-avatar';
        avatar.textContent = comment.username.charAt(0).toUpperCase();
        const bubble = document.createElement('div');
        bubble.className = 'comment-bubble';
        const author = document.createElement('strong');
        author.textContent = comment.username;
        const body = document.createElement('p');
        body.textContent = comment.body;
        const time = document.createElement('time');
        time.dateTime = comment.created_at;
        time.textContent = new Date(comment.created_at).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
        bubble.append(author, body, time);
        item.append(avatar, bubble);
        thread.insertBefore(item, form);
        thread.scrollTop = thread.scrollHeight;
        textarea.value = '';
        textarea.style.height = 'auto';
        if (trigger) {
          trigger.dataset.commentCount = String(comment.comment_count);
          trigger.setAttribute('aria-label', 'Open comments. ' + comment.comment_count + (comment.comment_count === 1 ? ' comment.' : ' comments.'));
        }
      } catch (error) {
        let status = dialog?.querySelector('[data-comment-error]');
        if (!status && dialog) {
          status = document.createElement('p');
          status.dataset.commentError = '';
          status.className = 'chai-chat-error';
          status.setAttribute('role', 'status');
          form.insertAdjacentElement('beforebegin', status);
        }
        if (status) status.textContent = error.message;
      } finally {
        submitButton.disabled = false;
      }
    });
  });

  document.querySelectorAll('[data-chai-chat]').forEach((chat) => {
    const feed = chat.querySelector('[data-chat-feed]');
    const form = chat.querySelector('[data-chat-form]');
    const status = chat.querySelector('[data-chat-status]');
    const error = chat.querySelector('[data-chat-error]');
    if (!feed || !form) return;
    let latestId = Number(chat.dataset.latestId || 0);
    let polling = false;

    const appendMessage = (message) => {
      if (message.id <= latestId) return;
      feed.querySelector('[data-chat-empty]')?.remove();
      const item = document.createElement('article');
      item.className = 'chai-message' + (String(message.user_id) === chat.dataset.userId ? ' is-mine' : '');
      item.dataset.messageId = String(message.id);
      const meta = document.createElement('div');
      meta.className = 'chai-message-meta';
      const author = document.createElement('strong');
      author.textContent = message.username;
      const time = document.createElement('time');
      time.dateTime = message.created_at;
      time.textContent = new Date(message.created_at).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
      const body = document.createElement('p');
      body.className = 'chai-message-body';
      body.textContent = message.body;
      meta.append(author, time);
      item.append(meta, body);
      feed.append(item);
      latestId = message.id;
      chat.dataset.latestId = String(latestId);
      feed.scrollTop = feed.scrollHeight;
    };

    const refresh = async () => {
      if (polling || document.hidden) return;
      polling = true;
      try {
        const response = await fetch(chat.dataset.endpoint + '?after=' + latestId, {
          headers: {'Accept': 'application/json'},
          credentials: 'same-origin',
          cache: 'no-store'
        });
        if (!response.ok) throw new Error('Reconnect');
        const result = await response.json();
        result.messages.forEach(appendMessage);
        if (status) status.textContent = 'Messages refresh automatically';
        if (error) error.hidden = true;
      } catch (_error) {
        if (status) status.textContent = 'Reconnecting…';
      } finally {
        polling = false;
      }
    };

    feed.scrollTop = feed.scrollHeight;
    refresh();
    window.setInterval(refresh, 4000);

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const field = form.querySelector('textarea[name="body"]');
      const button = form.querySelector('button[type="submit"]');
      if (!field || !button || !field.value.trim()) return;
      button.disabled = true;
      if (error) error.hidden = true;
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
          credentials: 'same-origin'
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Your message could not be sent.');
        appendMessage(result.message);
        field.value = '';
        field.style.height = 'auto';
        if (status) status.textContent = 'Messages refresh automatically';
      } catch (sendError) {
        if (error) {
          error.textContent = sendError.message;
          error.hidden = false;
        }
      } finally {
        button.disabled = false;
        field.focus();
      }
    });
  });


  const installButtons = document.querySelectorAll('[data-install-app]');
  const installStatus = document.querySelector('[data-install-status]');
  let installEvent = null;
  const hideInstall = () => installButtons.forEach((button) => { button.hidden = true; });
  if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
    hideInstall();
  }
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    installEvent = event;
    installButtons.forEach((button) => { button.hidden = false; });
  });
  window.addEventListener('appinstalled', () => {
    installEvent = null;
    hideInstall();
    if (installStatus) installStatus.textContent = 'Chai & Chatter is installed.';
  });
  installButtons.forEach((button) => button.addEventListener('click', async () => {
    if (!installEvent) {
      if (installStatus) installStatus.textContent = 'In Chrome, open ⋮ and choose “Install Chai & Chatter” or “Add to Home screen”.';
      return;
    }
    installEvent.prompt();
    const choice = await installEvent.userChoice;
    installEvent = null;
    if (choice.outcome === 'accepted') hideInstall();
    else if (installStatus) installStatus.textContent = 'You can install it anytime from Chrome’s menu.';
  }));

  if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
    navigator.serviceWorker.register('/service-worker.js', {scope: '/'})
      .catch(() => {});
  }

});
