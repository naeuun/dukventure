document.addEventListener("DOMContentLoaded", function () {
  const editBtn = document.getElementById("editProfileBtn");
  const modal = document.getElementById("editModal");
  const closeBtn = document.getElementById("closeModalBtn");

  const nameDisplay = document.querySelector(".nickname");
  const nameInput = document.getElementById("nicknameInput");

  const profileImgDisplay = document.getElementById("profileImage");
  const previewImgDisplay = document.querySelector(".preview_img"); // 모달 미리보기

  // 파일 input 없으면 동적으로 생성
  let profileImgInput = document.getElementById("profileImageInput");
  if (!profileImgInput) {
    profileImgInput = document.createElement("input");
    profileImgInput.type = "file";
    profileImgInput.id = "profileImageInput";
    profileImgInput.accept = "image/*";
    profileImgInput.style.display = "none";
    document.body.appendChild(profileImgInput);
  }
  // 모달 열기
  editBtn.addEventListener("click", () => {
    nameInput.value = nameDisplay.textContent.trim();
    modal.style.display = "flex"; // 클릭할 때만 나타남
  });

  // 모달 닫기
  closeBtn.addEventListener("click", () => {
    modal.style.display = "none"; // 닫기
  });

  // 닉네임 입력 즉시 반영
  nameInput.addEventListener("input", () => {
    nameDisplay.textContent = nameInput.value;
  });

  // 이미지 편집 버튼 클릭 → 파일 선택
  const imageEditBtn = document.querySelector(".image-edit-btn");
  if (imageEditBtn) {
    imageEditBtn.addEventListener("click", () => {
      profileImgInput.click();
    });
  }

  // 파일 선택 즉시 이미지 반영
  profileImgInput.addEventListener("change", () => {
    if (profileImgInput.files && profileImgInput.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        profileImgDisplay.src = e.target.result; // 프로필 이미지
        if (previewImgDisplay) {
          previewImgDisplay.src = e.target.result; // 모달 미리보기
        }
      };
      reader.readAsDataURL(profileImgInput.files[0]);
    }
  });
});
