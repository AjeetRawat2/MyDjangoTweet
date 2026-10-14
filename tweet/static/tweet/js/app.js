document.addEventListener('DOMContentLoaded', () => {
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
});

