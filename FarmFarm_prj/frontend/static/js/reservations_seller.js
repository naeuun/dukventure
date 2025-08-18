document.addEventListener("DOMContentLoaded", () => {
  const acceptBtns = document.querySelectorAll(".accept-btn");
  const rejectBtns = document.querySelectorAll(".reject-btn");
  const modals = document.querySelectorAll(".modal");


  const modal = document.querySelector(".modal");
  const closeModal = modal.querySelector(".close-btn");
  const confirmReject = modal.querySelector(".confirm-btn");
  let selectedReason = "";
  let currentRejectBtn = null; // 어떤 rejectBtn 눌렀는지 기억

  // 수락 버튼 이벤트
  acceptBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.textContent = "수락 완료";
      btn.classList.add("completed");
      // 같은 그룹의 reject 버튼 숨기기
      const siblingRejectBtn = btn.parentElement.querySelector(".reject-btn");
      if (siblingRejectBtn) {
        siblingRejectBtn.style.display = "none";
        siblingRejectBtn.disabled = true;
      }
    });
  });

  // 거절 버튼 클릭 → 모달 열기
  rejectBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      modal.style.display = "flex";
      selectedReason = "";
      currentRejectBtn = btn; // 현재 눌린 거절 버튼 기억
      // 기존 선택 초기화
      modal
        .querySelectorAll(".reason-btn")
        .forEach((b) => b.classList.remove("selected"));
    });
  });

  // 모달 닫기
  closeModal.addEventListener("click", () => {
    modal.style.display = "none";
    selectedReason = "";
    modal
      .querySelectorAll(".reason-btn")
      .forEach((b) => b.classList.remove("selected"));
    currentRejectBtn = null;
  });

  // 거절 사유 선택
  modal.querySelectorAll(".reason-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      modal
        .querySelectorAll(".reason-btn")
        .forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      selectedReason = btn.textContent;
    });
  });

  // 거절 확인
  confirmReject.addEventListener("click", () => {
    if (!selectedReason) {
      alert("거절 사유를 선택하세요.");
      return;
    }
    if (!currentRejectBtn) return;

    currentRejectBtn.textContent = "거절 완료";
    currentRejectBtn.classList.add("completed");
    // 같은 그룹 accept 버튼 숨기기
    const siblingAcceptBtn =
      currentRejectBtn.parentElement.querySelector(".accept-btn");
    if (siblingAcceptBtn) {
      siblingAcceptBtn.disabled = true;
      siblingAcceptBtn.style.display = "none";
    }

    modal.style.display = "none";
    selectedReason = "";
    currentRejectBtn = null;
  });
});
