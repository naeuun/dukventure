let map;

document.addEventListener("DOMContentLoaded", function () {
  const searchBtn = document.getElementById("searchBtn");
  const mapEl = document.getElementById("map");
  const toggleHugger = document.querySelector(".toggle_hugger");
  const firstSight = document.querySelector(".firstsight");

  // 검색 버튼 클릭 시 지도/토글 표시, 첫 화면 숨김
  searchBtn.addEventListener("click", () => {
    mapEl.style.display = "block";
    toggleHugger.style.display = "flex";
    firstSight.style.display = "none";
    if (map) {
      map.relayout();
      map.setCenter(new kakao.maps.LatLng(37.6495, 127.0141));
    }
  });

  if (typeof kakao !== "undefined" && kakao.maps) {
    const container = document.getElementById("map");
    const options = {
      center: new kakao.maps.LatLng(37.6495, 127.0141),
      level: 3,
    };
    map = new kakao.maps.Map(container, options);

    const imageSize = new kakao.maps.Size(20, 20);
    const imageOption = { offset: new kakao.maps.Point(20, 40) };
    const markerImage = new kakao.maps.MarkerImage(
      markerImageSrc,
      imageSize,
      imageOption
    );

    const keywordButtons = document.querySelectorAll(".per_foods");
    const searchInput = document.getElementById("searchInput");

    keywordButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        searchInput.value = btn.textContent.trim().replace(/^#/, "");
      });
    });

    const stores = [
      {
        name: "가게1",
        lat: 37.6495,
        lng: 127.0141,
        img: "/static/img/dummy_egg.png",
      },
      {
        name: "가게2",
        lat: 37.6495,
        lng: 127.0151,
        img: "/static/img/dummy_egg.png",
      },
    ];

    const markers = [];
    const customOverlays = [];

    const toggleBox = document.getElementById("toggleBox");
    const toggleButton = document.getElementById("toggleButton");
    const bottomSheet = document.getElementById("bottomSheet");

    // stores마다 마커 + 커스텀 오버레이 생성
    stores.forEach((store, i) => {
      const position = new kakao.maps.LatLng(store.lat, store.lng);
      const marker = new kakao.maps.Marker({
        map,
        position,
        title: store.name,
        image: markerImage,
      });
      markers.push(marker);

      const content = `
        <div class="custom-overlay-box">
          <img src="${store.img}" class="perimg" data-index="${i}">
        </div>
      `;

      const customOverlay = new kakao.maps.CustomOverlay({
        position: position,
        content: content,
        map: null, // 처음엔 안 보이게
        yAnchor: 1,
      });
      customOverlays.push(customOverlay);

      // 마커 클릭 시 (토글 활성 중이면) 오버레이 보이기 & 바텀시트 열기
      kakao.maps.event.addListener(marker, "click", () => {
        if (toggleBox.classList.contains("active")) {
          customOverlay.setMap(map);
          openBottomSheet();
        }
      });
    });

    // 토글 버튼 클릭 시 오버레이 on/off
    toggleBox.addEventListener("click", () => {
      toggleBox.classList.toggle("active");
      toggleButton.classList.toggle("active");

      if (toggleBox.classList.contains("active")) {
        customOverlays.forEach((overlay) => overlay.setMap(map));
        if (markers.length > 0) map.setCenter(markers[0].getPosition());
      } else {
        customOverlays.forEach((overlay) => overlay.setMap(null));
      }
    });

    // document 전체에서 perimg 클릭 감지
    document.body.addEventListener("click", (e) => {
      if (e.target.classList.contains("perimg")) {
        openBottomSheet();
      }
    });

    function openBottomSheet() {
      bottomSheet.classList.remove("hidden");
      bottomSheet.classList.add("show");
      applyManyItemsStoreMargin();
    }

    function hideBottomSheet() {
      bottomSheet.classList.remove("show", "expanded");
      bottomSheet.classList.add("hidden");
    }

    // many_items_store 위치 확인 후 margin 적용
    function applyManyItemsStoreMargin() {
      const sheetContent = bottomSheet.querySelector(".sheet_content_v2");
      if (!sheetContent) return;

      const manyItemsStores =
        sheetContent.querySelectorAll(".many_items_store");
      if (manyItemsStores.length === 0) return;

      const lastElement = sheetContent.lastElementChild;
      manyItemsStores.forEach((store) => {
        store.style.marginBottom = "";
        if (store === lastElement) {
          const huggerElements = document.getElementsByClassName("per_stores");
          const hugger = huggerElements[huggerElements.length - 1];
          hugger.style.marginBottom = "0px";
          store.style.marginBottom = "130px";
        }
      });
    }

    // 바텀시트 터치 드래그로 확장/축소 및 숨기기 기능
    let isDragging = false;
    let startY = 0;

    bottomSheet.addEventListener("touchstart", (e) => {
      startY = e.touches[0].clientY;
      isDragging = true;
    });

    bottomSheet.addEventListener("touchmove", (e) => {
      if (!isDragging) return;
      const moveY = e.touches[0].clientY;
      const diffY = startY - moveY;

      if (diffY > 30 && !bottomSheet.classList.contains("expanded")) {
        bottomSheet.classList.add("expanded");
      } else if (diffY < -30 && bottomSheet.classList.contains("expanded")) {
        bottomSheet.classList.remove("expanded");
      }
    });

    bottomSheet.addEventListener("touchend", (e) => {
      const endY = e.changedTouches[0].clientY;
      const diffY = startY - endY;
      isDragging = false;

      if (diffY < -400) {
        hideBottomSheet();
      }
    });

    // 바텀시트 내 스크롤 이벤트
    const sheetContent = document.querySelector(".sheet_content_v2");
    let lastScrollTop = 0;
    let isExpanded = false;

    sheetContent.addEventListener("scroll", () => {
      const currentScrollTop = sheetContent.scrollTop;

      if (currentScrollTop > lastScrollTop) {
        if (!isExpanded) {
          bottomSheet.classList.add("expanded");
          isExpanded = true;
        }
      } else {
        if (isExpanded) {
          bottomSheet.classList.remove("expanded");
          isExpanded = false;
        }
      }

      lastScrollTop = currentScrollTop <= 0 ? 0 : currentScrollTop;
    });

    // 지도 클릭 시 바텀시트 숨기기
    container.addEventListener("click", () => {
      hideBottomSheet();
    });

    // 수량/시간 조절 이벤트
    document.querySelectorAll(".per_stores").forEach((store) => {
      const minusBtn = store.querySelector(".minusBtn");
      const plusBtn = store.querySelector(".plusBtn");
      const quantitySpan = store.querySelector(".quantity");
      const hourInput = store.querySelector(".hourInput");
      const minuteInput = store.querySelector(".minuteInput");

      let quantity = 0;

      minusBtn.addEventListener("click", () => {
        if (quantity > 0) {
          quantity--;
          quantitySpan.textContent = quantity;
        }
      });

      plusBtn.addEventListener("click", () => {
        quantity++;
        quantitySpan.textContent = quantity;
      });

      hourInput.addEventListener("input", () => {
        if (hourInput.value > 23) hourInput.value = 23;
        if (hourInput.value < 0) hourInput.value = 0;
      });

      minuteInput.addEventListener("input", () => {
        if (minuteInput.value > 59) minuteInput.value = 59;
        if (minuteInput.value < 0) minuteInput.value = 0;
      });
    });
  } else {
    document.getElementById("errorMessage").innerHTML =
      "카카오맵을 불러올 수 없습니다.<br>API 키를 확인해주세요.";
  }
});
