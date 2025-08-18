// static/js/consumer_home/character_home.js
document.addEventListener('DOMContentLoaded', function () {
  // 연필(열기) 버튼: .information_detail의 "직계 자식"인 .edit만 선택
  const editBtn = document.querySelector('.information_detail > .edit');
  const pop = document.querySelector('.information_detail .name-edit-popover');
  const input = pop ? pop.querySelector('.name-input') : null;
  const btnSave = pop ? pop.querySelector('.name-pop-save') : null;
  const btnClose = pop ? pop.querySelector('.name-pop-close') : null;
  const nameText = document.querySelector('.information_detail .cha_nic');

  if (!editBtn || !pop || !input || !btnSave || !btnClose || !nameText) {
    console.warn('[character_home] popover elements not found');
    return;
  }

  const open = () => {
    pop.classList.add('show');
    input.value = (nameText.textContent || '').trim();
    setTimeout(() => input.focus(), 0);
  };

  const close = () => pop.classList.remove('show');

  const save = () => {
    const v = input.value.trim();
    if (!v) return;
    nameText.textContent = v;
    close();
  };

  // 팝업 열기/토글
  editBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    pop.classList.contains('show') ? close() : open();
  });

  // 닫기/저장
  btnClose.addEventListener('click', (e) => { e.stopPropagation(); close(); });
  btnSave.addEventListener('click',  (e) => { e.stopPropagation(); save(); });

  // Enter 저장 / Esc 닫기
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') save();
    if (e.key === 'Escape') close();
  });

  // 바깥 클릭 시 닫기
  document.addEventListener('click', (e) => {
    if (!pop.classList.contains('show')) return;
    if (!pop.contains(e.target) && e.target !== editBtn) close();
  });
});
