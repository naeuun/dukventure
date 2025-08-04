document.addEventListener("DOMContentLoaded", function () {
  const acceptBtn = document.getElementById("accept");
  const refuseBtn = document.getElementById("refuse");
  const modal = document.getElementById("refuseModal");
  const reasonBtns = document.querySelectorAll(".reason_btn");
  const reservDetails = document.querySelector(".reserv_details");

  // 수락 버튼 클릭 시
  acceptBtn.addEventListener("click", function () {
    // 기존에 "결과 문구"가 있으면 제거하고 새로 추가
    removeResultText();
    const result = document.createElement("p");
    result.classList.add("result_text");
    result.textContent = "수락됨";
    reservDetails.appendChild(result);
  });

  // 거절 버튼 클릭 시
  refuseBtn.addEventListener("click", function () {
    modal.classList.toggle("hidden");
  });

  // 거절 사유 선택 시
  reasonBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      removeResultText();
      const reason = this.dataset.reason;
      const result = document.createElement("p");
      result.classList.add("result_text");
      result.textContent = `거절됨 : ${reason}`;
      reservDetails.appendChild(result);
      modal.classList.add("hidden");
    });
  });

  // 기존 결과 텍스트가 있으면 삭제하는 함수
  function removeResultText() {
    const existing = reservDetails.querySelector(".result_text");
    if (existing) existing.remove();
  }
});
