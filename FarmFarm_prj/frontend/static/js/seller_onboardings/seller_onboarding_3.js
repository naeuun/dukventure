/* 음성인식에 대한 js를 넣을 예정입니다. */
document.addEventListener("DOMContentLoaded", () => {
  const requiredIndexes = [1, 2, 3, 5, 6, 7];
  const requiredFields = requiredIndexes.map((i) =>
    document.getElementById(`field${i}`)
  );
  const registerBtn = document.querySelector(".register_button");
  setDisabledState(true);
  requiredFields.forEach((el) => {
    if (!el) return;
    el.addEventListener("input", checkFilled);
    el.addEventListener("change", checkFilled);
  });
  if (registerBtn) {
    registerBtn.addEventListener("click", (e) => {
      if (registerBtn.disabled) {
        e.stopImmediatePropagation();
        e.preventDefault();
        return;
      }
      location.href = "selleronboarding5";
    });
  }
  checkFilled();
  function checkFilled() {
    const allFilled = requiredFields.every((el) => {
      if (!el) return false;
      const type = el.type ? el.type.toLowerCase() : "";
      if (type === "file") {
        return el.files && el.files.length > 0;
      }
      const val = (el.value || "").trim();
      return val.length > 0;
    });
    setDisabledState(!allFilled);
  }
  function setDisabledState(disabled) {
    if (!registerBtn) return;
    if (disabled) {
      registerBtn.disabled = true;
      registerBtn.classList.remove("enabled");
      registerBtn.style.cursor = "not-allowed";
    } else {
      registerBtn.disabled = false;
      registerBtn.classList.add("enabled");
      registerBtn.style.cursor = "pointer";
    }
  }
  const micBtn = document.querySelector(".voice_recognition_btn");
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
  const recogBtn = document.querySelector(".voice_recognizing_btn");
  const micImg = recogBtn
    ? recogBtn.querySelector("img.voice_modal_mic")
    : null;
  if (recogBtn && micImg) {
    const originalSrc = micImg.src;
    let pressedSrc =
      micImg.dataset && micImg.dataset.pressedSrc
        ? micImg.dataset.pressedSrc
        : null;
    if (!pressedSrc) {
      try {
        pressedSrc = originalSrc.replace("mic_neon", "mic");
      } catch (e) {
        pressedSrc = originalSrc;
      }
    }
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
      // 녹음 로직 호출하기
    }
    function endPress(cancel = false) {
      if (!pressing) return;
      pressing = false;
      recogBtn.classList.remove("recording");
      micImg.src = originalSrc;
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
        e.preventDefault();
        startPress();
      },
      { passive: false }
    );
    document.addEventListener(
      "touchmove",
      (e) => {
        if (!pressing || touchId === null) return;
        for (let i = 0; i < e.changedTouches.length; i++) {
          const t = e.changedTouches[i];
          if (t.identifier === touchId) {
            if (!isPointInside(recogBtn, t.clientX, t.clientY)) {
              endPress(true);
              touchId = null;
            }
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
      for (let i = 0; i < e.changedTouches.length; i++) {
        const t = e.changedTouches[i];
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
  // --- 가게 사진 업로드 UI (라벨 밖 아이콘도 숨김) ---
  // --- 가게 사진 업로드 UI (아이콘만 숨기고 라벨 텍스트는 유지) ---
  (function () {
    let fileInput = document.getElementById("field9");
    if (!fileInput) return;

    const fileLabel = document.querySelector('label[for="field9"]');

    // 아이콘 요소들만 선택 (라벨 밖에 있어도 전부)
    const allUploadIcons = Array.from(
      document.querySelectorAll(".upload_icon")
    );

    let infoWrap = document.querySelector(".file_info_wrap");
    if (!infoWrap) {
      infoWrap = document.createElement("div");
      infoWrap.className = "file_info_wrap";
      if (fileLabel && fileLabel.parentNode)
        fileLabel.parentNode.insertBefore(infoWrap, fileLabel.nextSibling);
      else if (fileInput && fileInput.parentNode)
        fileInput.parentNode.insertBefore(infoWrap, fileInput.nextSibling);
    }

    function hideAllUploadIcons() {
      allUploadIcons.forEach((el) => {
        el.style.display = "none";
      });
    }

    function showAllUploadIcons() {
      allUploadIcons.forEach((el) => {
        el.style.display = "";
      });
    }

    function renderFileState() {
      infoWrap.innerHTML = "";

      if (fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];

        hideAllUploadIcons();

        const nameEl = document.createElement("span");
        nameEl.className = "file_name";
        nameEl.textContent = file.name;

        const delBtn = document.createElement("button");
        delBtn.type = "button";
        delBtn.className = "delete_file_btn";
        delBtn.setAttribute("aria-label", "사진 삭제");
        delBtn.textContent = "삭제";

        delBtn.addEventListener("click", (e) => {
          e.preventDefault();
          try {
            const newInput = fileInput.cloneNode(true);
            newInput.value = "";
            newInput.addEventListener("change", renderFileState);
            fileInput.parentNode.replaceChild(newInput, fileInput);
            fileInput = newInput;
          } catch (err) {
            try {
              fileInput.value = "";
            } catch (e) {}
          }
          infoWrap.innerHTML = "";
          showAllUploadIcons();
        });

        infoWrap.appendChild(nameEl);
        infoWrap.appendChild(delBtn);
      } else {
        showAllUploadIcons();
        infoWrap.innerHTML = "";
      }
    }

    renderFileState();
    fileInput.addEventListener("change", renderFileState);
  })();
});
