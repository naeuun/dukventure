document.addEventListener("DOMContentLoaded", () => {
  // --- 이미지 변경 ---
  const changePhotoBtn = document.querySelector(".change_photo_btn");
  const fileInput = document.getElementById("change_photo_input");
  const productImg = document.querySelector(".product-img");

  if (changePhotoBtn && fileInput && productImg) {
    changePhotoBtn.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => (productImg.src = e.target.result);
        reader.readAsDataURL(file);
      }
    });
  }

  // --- 음성 인식 모달 ---
  const micBtn = document.querySelector(".voice_recognization_btn"); // 모달 여는 버튼
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

  // --- 모달 안 마이크 버튼 누름 상태 ---
  const recogBtn = document.querySelector(".voice_recognizing_btn");
  const micImg = recogBtn?.querySelector("img.voice_modal_mic");
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
      // 🔴 여기서 녹음 시작 로직 실행
    }
    function endPress(cancel = false) {
      if (!pressing) return;
      pressing = false;
      recogBtn.classList.remove("recording");
      micImg.src = originalSrc;
      // 🔴 여기서 녹음 종료 로직 실행
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
});
