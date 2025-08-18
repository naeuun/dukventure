document.addEventListener("DOMContentLoaded", () => {
  // --- 등록 버튼 ---
  const registerBtn = document.querySelector(".register_btn");
  if (registerBtn) {
    registerBtn.addEventListener("click", (e) => {
      if (registerBtn.disabled) {
        e.preventDefault();
        e.stopImmediatePropagation();
        return;
      }
    });
  }

  // --- 음성 인식 모달 토글 ---
  const micBtn = document.querySelector(".voice_recognization .circle_btn");
  const modal = document.querySelector(".voice_modal");
  const closeModalBtn = document.querySelector(".voice_modal_close");
  const overlay = document.querySelector(".voice_modal_overlay");

  if (micBtn && modal) {
    micBtn.addEventListener("click", () => modal.classList.remove("hidden"));
  }
  if (closeModalBtn && modal) {
    closeModalBtn.addEventListener("click", () =>
      modal.classList.add("hidden")
    );
  }
  if (overlay && modal) {
    overlay.addEventListener("click", () => modal.classList.add("hidden"));
  }

  // --- 음성 인식 버튼 누름 상태 토글 ---
  const recogBtn = document.querySelector(".voice_recognizing_btn");
  const micImg = recogBtn
    ? recogBtn.querySelector("img.voice_modal_mic")
    : null;
  if (recogBtn && micImg) {
    const originalSrc = micImg.src;
    const pressedSrc =
      micImg.dataset.pressedSrc || originalSrc.replace("mic_neon", "mic");
    let pressing = false;
    let touchId = null;

    function isPointInside(el, x, y) {
      const r = el.getBoundingClientRect();
      return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
    }

    function startPress() {
      if (pressing) return;
      pressing = true;
      recogBtn.classList.add("recording");
      micImg.src = pressedSrc;
      // 녹음 시작 로직
    }
    function endPress(cancel = false) {
      if (!pressing) return;
      pressing = false;
      recogBtn.classList.remove("recording");
      micImg.src = originalSrc;
      // 녹음 종료 로직
    }

    recogBtn.addEventListener("mousedown", (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      startPress();
    });
    document.addEventListener("mouseup", (e) => {
      if (e.button !== 0) return;
      endPress();
    });
    document.addEventListener("mousemove", (e) => {
      if (!pressing) return;
      if (!isPointInside(recogBtn, e.clientX, e.clientY)) endPress(true);
    });

    recogBtn.addEventListener(
      "touchstart",
      (e) => {
        const t = e.changedTouches[0];
        touchId = t.identifier;
        if (e.cancelable) e.preventDefault();
        startPress();
      },
      { passive: false }
    );

    document.addEventListener(
      "touchmove",
      (e) => {
        if (!pressing || touchId === null) return;
        for (const t of e.changedTouches) {
          if (
            t.identifier === touchId &&
            !isPointInside(recogBtn, t.clientX, t.clientY)
          ) {
            endPress(true);
            touchId = null;
            break;
          }
        }
      },
      { passive: true }
    );

    document.addEventListener("touchend", (e) => {
      if (!pressing || touchId === null) {
        touchId = null;
        return;
      }
      for (const t of e.changedTouches) {
        if (t.identifier === touchId) {
          endPress();
          touchId = null;
          break;
        }
      }
    });

    document.addEventListener("touchcancel", () => {
      if (pressing) endPress(true);
      touchId = null;
    });
  }

  // --- 이미지 업로드 UI 제어 (아이콘 숨기기 포함) ---
  const fileInput = document.getElementById("field9");
  const fileInfoWrap = document.querySelector(".file_info_wrap");
  const fileNameSpan = fileInfoWrap
    ? fileInfoWrap.querySelector(".file_name")
    : null;
  const deleteBtn = fileInfoWrap
    ? fileInfoWrap.querySelector(".delete_file_btn")
    : null;
  const balloon = document.querySelector(".text_box_text");
  const uploadLabel = document.querySelector(".upload_label"); // 업로드 아이콘

  if (
    fileInput &&
    fileInfoWrap &&
    fileNameSpan &&
    deleteBtn &&
    balloon &&
    uploadLabel
  ) {
    function updateFileUI() {
      if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileNameSpan.textContent = file.name;
        fileInfoWrap.style.display = "inline-flex";
        balloon.style.display = "none"; // 말풍선 숨김
        uploadLabel.style.display = "none"; // 업로드 아이콘 숨김
      } else {
        fileInfoWrap.style.display = "none";
        balloon.style.display = "block"; // 말풍선 보임
        uploadLabel.style.display = "inline-block"; // 업로드 아이콘 보임
      }
    }

    fileInput.addEventListener("change", updateFileUI);
    deleteBtn.addEventListener("click", () => {
      fileInput.value = "";
      updateFileUI();
    });

    // 초기 상태 반영 (이미 등록된 사진이 있을 경우)
    updateFileUI();
  }

  // --- 키워드 최대 3개 선택 (클래스 & 체크박스 통합) ---
  const keywordOptions = document.querySelectorAll(".keyword-option");
  const checkboxes = document.querySelectorAll(
    '.keyword-option input[type="checkbox"]'
  );

  function enforceMaxSelection(option = null, checkbox = null) {
    const selected = document.querySelectorAll(".keyword-option.selected");
    const checkedCount = document.querySelectorAll(
      '.keyword-option input[type="checkbox"]:checked'
    ).length;

    if (option) {
      if (option.classList.contains("selected")) {
        option.classList.remove("selected");
      } else if (selected.length < 3) {
        option.classList.add("selected");
      }
    }
    if (checkbox && checkedCount > 3) {
      checkbox.checked = false;
      alert("최대 3개까지만 선택할 수 있습니다.");
    }
  }

  keywordOptions.forEach((option) =>
    option.addEventListener("click", () => enforceMaxSelection(option))
  );
  checkboxes.forEach((cb) =>
    cb.addEventListener("change", () => enforceMaxSelection(null, cb))
  );

  // --- 등록 후 웰컴 모달 ---
  const welcomeContent = document.querySelector(".welcome_content");
  const welcomeOverlay = document.querySelector(".welcome_overlay");

  if (registerBtn && welcomeContent && welcomeOverlay) {
    registerBtn.addEventListener("click", (e) => {
      if (registerBtn.disabled) return;

      welcomeOverlay.style.display = "block";
      welcomeContent.style.display = "flex";
      document.body.style.overflow = "hidden";

      e.preventDefault();

      setTimeout(() => {
        window.location.href = "/storescustomer";
      }, 1000);
    });

    welcomeOverlay.addEventListener("click", () => {
      welcomeOverlay.style.display = "none";
      welcomeContent.style.display = "none";
      document.body.style.overflow = "";
    });
  }
});
