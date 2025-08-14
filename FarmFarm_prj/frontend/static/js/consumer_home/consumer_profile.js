document.addEventListener("DOMContentLoaded", function() {
    const editBtn = document.getElementById("editProfileBtn");
    const modal = document.getElementById("editModal");
    const closeBtn = document.getElementById("closeModalBtn");
    const saveBtn = document.getElementById("saveProfileBtn");

    const nameDisplay = document.querySelector(".nickname");
    const nameInput = document.getElementById("nicknameInput");

    const profileImgDisplay = document.getElementById("profileImage");
    const profileImgInput = document.getElementById("profileImageInput");

    // 모달 열기
    editBtn.addEventListener("click", () => {
      nameInput.value = nameDisplay.textContent.trim();
      modal.style.display = "flex";
    });

    // 모달 닫기
    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });

    // 저장 버튼
    saveBtn.addEventListener("click", () => {
      nameDisplay.textContent = nameInput.value;

      // 선택한 이미지가 있으면 미리보기 변경
      if (profileImgInput.files && profileImgInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
          profileImgDisplay.src = e.target.result;
        }
        reader.readAsDataURL(profileImgInput.files[0]);
      }

      modal.style.display = "none";
    });
  });