document.addEventListener("DOMContentLoaded", function () {
  const openBtn = document.getElementById("benefits");
  const modal = document.getElementById("benefitModal");
  const closeBtn = modal.querySelector(".modal-close");
  let lastFocused = null;
  let focusable = [];
  let firstFocusable = null;
  let lastFocusable = null;
  let boundKeydown = null;

  // 유틸: 모달 안의 포커스 가능한 요소들 찾기
  function updateFocusable() {
    focusable = Array.from(
      modal.querySelectorAll(
        'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    );
    firstFocusable = focusable[0] || closeBtn;
    lastFocusable = focusable[focusable.length - 1] || closeBtn;
  }

  function trapTabKey(e) {
    if (e.key !== "Tab") return;

    // shift+tab
    if (e.shiftKey) {
      if (document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      }
    } else {
      if (document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  }

  function openModal() {
    // 저장해둔 마지막 포커스(복귀용)
    lastFocused = document.activeElement;

    // 보이기
    modal.style.display = "block";
    requestAnimationFrame(() => modal.classList.add("show"));

    // aria-hidden 해제 (스크린리더에 보이게)
    modal.setAttribute("aria-hidden", "false");

    // 포커스 가능한 요소 갱신 후 닫기 버튼으로 포커스 이동
    updateFocusable();
    // 안전하게 잠깐 delay 후 포커스 이동 (transition과 충돌 방지)
    setTimeout(() => {
      closeBtn.focus();
    }, 50);

    // 키다운 리스너 바인딩 (탭 트랩 및 ESC)
    boundKeydown = function (e) {
      if (e.key === "Escape") {
        closeModal();
        return;
      }
      trapTabKey(e);
    };
    document.addEventListener("keydown", boundKeydown);

    // 페이지 스크롤이 뒤로 안가게 (선택적)
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    // 모달 닫기 애니메이션 시작
    modal.classList.remove("show");

    // aria-hidden 처리 (스크린리더에서 숨김)
    modal.setAttribute("aria-hidden", "true");

    // 키다운 리스너 제거
    if (boundKeydown) {
      document.removeEventListener("keydown", boundKeydown);
      boundKeydown = null;
    }

    // 포커스 정리: 모달 내부 포커스 제거
    if (document.activeElement && modal.contains(document.activeElement)) {
      try {
        document.activeElement.blur();
      } catch (e) {
        /* ignore */
      }
    }

    // 애니메이션 끝난 뒤 완전 숨김 및 포커스 복귀
    setTimeout(() => {
      modal.style.display = "none";
      // 원래 버튼으로 포커스 복귀 (존재하면)
      if (lastFocused && typeof lastFocused.focus === "function") {
        lastFocused.focus();
      } else {
        openBtn.focus();
      }
      // 페이지 스크롤 복원
      document.body.style.overflow = "";
    }, 190);
  }

  openBtn.addEventListener("click", openModal);
  closeBtn.addEventListener("click", closeModal);

  // 모달 패널 바깥 클릭하면 닫기
  modal.addEventListener("click", function (e) {
    // 클릭 대상이 오버레이(modal)일 때만 닫기
    if (e.target === modal) closeModal();
  });

  // (안전장치) 링크나 버튼 등으로 포커스가 modal 내부로 들어갈 경우 포커스 목록 갱신
  modal.addEventListener("focusin", updateFocusable);
});
