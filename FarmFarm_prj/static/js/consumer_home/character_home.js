document.addEventListener('DOMContentLoaded', function () {
  const openBtn = document.querySelector('.information_detail .name-pop-open'); // ✅ 수정
  const pop = document.querySelector('.information_detail .name-edit-popover');
  const input = pop?.querySelector('.name-input');
  const btnSave = pop?.querySelector('.name-pop-save');
  const btnClose = pop?.querySelector('.name-pop-close');
  const nameText = document.querySelector('.information_detail .cha_nic');

  if (!openBtn || !pop || !input || !btnSave || !btnClose || !nameText) {
    console.warn('[character_home] popover elements not found');
    return;
  }

  const open = () => {
    pop.classList.add('show');
    input.value = (nameText.textContent || '').trim();
    setTimeout(() => input.focus(), 0);
  };
  const close = () => pop.classList.remove('show');
  const save = () => { const v = input.value.trim(); if (!v) return; nameText.textContent = v; close(); };

  openBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    pop.classList.contains('show') ? close() : open();
  });
  btnClose.addEventListener('click', (e) => { e.stopPropagation(); close(); });
  btnSave.addEventListener('click', (e) => { e.stopPropagation(); save(); });
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') save(); if (e.key === 'Escape') close(); });

  // 바깥 클릭시 닫기 (열기 버튼을 포함한 영역 제외)
  document.addEventListener('click', (e) => {
    if (!pop.classList.contains('show')) return;
    if (!pop.contains(e.target) && !openBtn.contains(e.target)) close(); // ✅ 수정
  });
});
