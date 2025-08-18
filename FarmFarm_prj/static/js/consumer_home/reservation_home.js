document.addEventListener('DOMContentLoaded', function () {
  const openBtn = document.getElementById('btn-review');
  const modal = document.getElementById('reviewModal');
  const closeBtn = document.getElementById('modalCloseBtn');

  const fileInput = document.getElementById('reviewPhoto');
  const changePhotoBtn = document.getElementById('changePhotoBtn');
  const changePhotoImg = document.getElementById('changePhotoImg');

  let savedScrollY = 0;

  function lockBodyScroll() {
    savedScrollY = window.scrollY || window.pageYOffset || 0;
    document.body.classList.add('body-lock');
    document.body.style.top = `-${savedScrollY}px`;
  }

  function unlockBodyScroll() {
    document.body.classList.remove('body-lock');
    document.body.style.top = '';
    window.scrollTo(0, savedScrollY);
  }

  function openModal() {
    if (!modal) return;
    modal.classList.add('is-open');
    lockBodyScroll();
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove('is-open');
    unlockBodyScroll();
  }

  if (openBtn) openBtn.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeModal();
    });
  }

  // 업로드 아이콘 → 파일 선택
  if (changePhotoBtn && fileInput) {
    changePhotoBtn.addEventListener('click', function () {
      fileInput.click();
    });
  }

  // 파일 선택 시 아이콘을 이미지로 변경
  if (fileInput && changePhotoImg) {
    fileInput.addEventListener('change', function () {
      const file = fileInput.files && fileInput.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function (e) {
        changePhotoImg.src = e.target.result;
      };
      reader.readAsDataURL(file);
    });
  }

  // 키워드 토글
  document.querySelectorAll('.modal__keywords .tag').forEach(function (el) {
    el.addEventListener('click', function () {
      el.classList.toggle('selected');
    });
  });
});
