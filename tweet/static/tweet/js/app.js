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

