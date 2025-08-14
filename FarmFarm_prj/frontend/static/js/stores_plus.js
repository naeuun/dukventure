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
    micBtn.addEventListener("click", () => {
      modal.classList.remove("hidden");
    });
  }
  if (closeModalBtn && modal) {
    closeModalBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
    });
  }
  if (overlay && modal) {
    overlay.addEventListener("click", () => {
      modal.classList.add("hidden");
    });
  }

  // --- 음성 인식 버튼 누름 상태 토글 ---
  const recogBtn = document.querySelector(".voice_recognizing_btn");
  const micImg = recogBtn
    ? recogBtn.querySelector("img.voice_modal_mic")
    : null;
  if (recogBtn && micImg) {
    const originalSrc = micImg.src;
    let pressedSrc =
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
      // 녹음 시작 로직 여기에 추가
    }
    function endPress(cancel = false) {
      if (!pressing) return;
      pressing = false;
      recogBtn.classList.remove("recording");
      micImg.src = originalSrc;
      // 녹음 종료 로직 여기에 추가
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
      if (!isPointInside(recogBtn, e.clientX, e.clientY)) {
        endPress(true);
      }
    });

    recogBtn.addEventListener(
      "touchstart",
      (e) => {
        const t = e.changedTouches[0];
        touchId = t.identifier;

        if (e.cancelable) {
          e.preventDefault(); // 스크롤 등 다른 동작을 막을 수 있을 때만
        }

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

  // --- 이미지 업로드 UI 제어 ---
  const fileInput = document.getElementById("field9");
  const fileInfoWrap = document.querySelector(".file_info_wrap");
  const fileNameSpan = fileInfoWrap.querySelector(".file_name");
  const deleteBtn = fileInfoWrap.querySelector(".delete_file_btn");
  const balloon = document.querySelector(".text_box_text");

  if (fileInput && fileInfoWrap && fileNameSpan && deleteBtn && balloon) {
    function updateFileUI() {
      if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileNameSpan.textContent = file.name;
        fileInfoWrap.style.display = "inline-flex";
        balloon.style.display = "none";
      } else {
        fileInfoWrap.style.display = "none";
        balloon.style.display = "block";
      }
    }
    fileInput.addEventListener("change", updateFileUI);
    deleteBtn.addEventListener("click", () => {
      fileInput.value = "";
      updateFileUI();
    });
    updateFileUI();
  }

  // --- 키워드 최대 3개 선택 ---
  const keywordOptions = document.querySelectorAll(".keyword-option");
  keywordOptions.forEach((option) => {
    option.addEventListener("click", () => {
      const selected = document.querySelectorAll(".keyword-option.selected");
      if (option.classList.contains("selected")) {
        option.classList.remove("selected");
      } else if (selected.length < 3) {
        option.classList.add("selected");
      }
    });
  
  const registerBtn = document.querySelector(".register_btn");
  const welcomeContent = document.querySelector(".welcome_content");
  const welcomeOverlay = document.querySelector(".welcome_overlay");

  if (registerBtn && welcomeContent && welcomeOverlay) {
    registerBtn.addEventListener("click", (e) => {
      if (registerBtn.disabled) {
        e.preventDefault();
        e.stopImmediatePropagation();
        return;
      }

      // 모달 띄우기
      welcomeOverlay.style.display = "block";
      welcomeContent.style.display = "flex";

      // 스크롤 막기
      document.body.style.overflow = "hidden";

      // 기본 폼 제출 막기 (필요하면 삭제)
      e.preventDefault();

      // 2초 뒤 이전 페이지로 이동
      setTimeout(() => {
        window.location.href = "/storescustomer";
      }, 1000);

    });
  }

  // 오버레이 클릭 시 모달 닫기 (선택사항)
  const welcomeOverlayEl = document.querySelector(".welcome_overlay");
  if (welcomeOverlayEl) {
    welcomeOverlayEl.addEventListener("click", () => {
      welcomeOverlayEl.style.display = "none";
      if (welcomeContent) welcomeContent.style.display = "none";
      document.body.style.overflow = "";
    });
  }
  });
});
