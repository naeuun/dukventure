let map;
let marker; // 검색 마커

document.addEventListener("DOMContentLoaded", function () {
  const container = document.getElementById("map");
  const bottomSheet = document.getElementById("bottomSheet");
  const searchBtn = document.getElementById("searchBtn");
  const searchInput = document.getElementById("searchInput");

  // 지도 초기화
  if (typeof kakao !== "undefined" && kakao.maps) {
    const options = {
      center: new kakao.maps.LatLng(37.6495, 127.0141),
      level: 3,
    };
    map = new kakao.maps.Map(container, options);

    const imageSize = new kakao.maps.Size(20, 20);
    const imageOption = { offset: new kakao.maps.Point(20, 40) };
    const markerImageSrc = "/static/img/stores.png";
    const markerImage = new kakao.maps.MarkerImage(
      markerImageSrc,
      imageSize,
      imageOption
    );

    const stores = [
      { name: "4.19민주역 달걀 할머니", lat: 37.6495, lng: 127.0141 },
      { name: "4.19민주역 달걀 할머니", lat: 37.6495, lng: 127.0151 },
    ];

    // 가게별 마커 생성
    stores.forEach((store) => {
      const position = new kakao.maps.LatLng(store.lat, store.lng);
      const storeMarker = new kakao.maps.Marker({
        map: map,
        position: position,
        title: store.name,
        image: markerImage,
      });

      kakao.maps.event.addListener(storeMarker, "click", () =>
        openBottomSheet()
      );
    });

    // 검색
    if (searchBtn && searchInput) {
      searchBtn.addEventListener("click", searchPlaces);
      searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") searchPlaces();
      });
    }

    function searchPlaces() {
      const keyword = searchInput.value.trim();
      if (!keyword) return alert("검색어를 입력하세요!");

      const filteredStores = stores.filter((store) =>
        store.name.includes(keyword)
      );
      if (filteredStores.length === 0) return alert("검색 결과가 없습니다.");

      if (marker) marker.setMap(null);

      const firstStore = filteredStores[0];
      const coords = new kakao.maps.LatLng(firstStore.lat, firstStore.lng);
      map.setCenter(coords);

      marker = new kakao.maps.Marker({
        position: coords,
        map: map,
        title: firstStore.name,
      });
      kakao.maps.event.addListener(marker, "click", () => openBottomSheet());
    }
  } else {
    document.getElementById("errorMessage").innerHTML =
      "카카오맵을 불러올 수 없습니다.<br>API 키를 확인해주세요.";
  }

  // 바텀시트 열기/닫기
  function openBottomSheet() {
    bottomSheet.classList.remove("hidden");
    bottomSheet.classList.add("show");
    applyManyItemsStoreMargin();
    bindPerStoreEvents(); // 동적 요소 이벤트 바인딩
  }

  function hideBottomSheet() {
    bottomSheet.classList.remove("show", "expanded");
    bottomSheet.classList.add("hidden");
  }

  // 바텀시트 터치 드래그
  let isDragging = false;
  let startY = 0;

  bottomSheet.addEventListener("touchstart", (e) => {
    startY = e.touches[0].clientY;
    isDragging = true;
  });

  bottomSheet.addEventListener("touchmove", (e) => {
    if (!isDragging) return;
    const diffY = startY - e.touches[0].clientY;

    if (diffY > 30 && !bottomSheet.classList.contains("expanded"))
      bottomSheet.classList.add("expanded");
    else if (diffY < -30 && bottomSheet.classList.contains("expanded"))
      bottomSheet.classList.remove("expanded");
  });

  bottomSheet.addEventListener("touchend", (e) => {
    isDragging = false;
    if (startY - e.changedTouches[0].clientY < -400) hideBottomSheet();
  });

  // 바텀시트 내 스크롤 제어
  const sheetContent = document.querySelector(".sheet_content_v2");
  let lastScrollTop = 0;
  let isExpanded = false;

  if (sheetContent) {
    sheetContent.addEventListener("scroll", () => {
      const currentScrollTop = sheetContent.scrollTop;
      if (currentScrollTop > lastScrollTop && !isExpanded) {
        bottomSheet.classList.add("expanded");
        isExpanded = true;
      } else if (currentScrollTop < lastScrollTop && isExpanded) {
        bottomSheet.classList.remove("expanded");
        isExpanded = false;
      }
      lastScrollTop = currentScrollTop <= 0 ? 0 : currentScrollTop;
    });
  }

  // 동적 이벤트 바인딩 (수량 및 시간)
  function bindPerStoreEvents() {
    const perStoresElements = document.querySelectorAll(".per_stores");
    perStoresElements.forEach((store) => {
      const minusBtn = store.querySelector(".minusBtn");
      const plusBtn = store.querySelector(".plusBtn");
      const quantitySpan = store.querySelector(".quantity");
      const timeInput = store.querySelector(".timeInput");
      let quantity = 0;

      minusBtn?.addEventListener("click", () => {
        if (quantity > 0) quantitySpan.textContent = --quantity;
      });

      plusBtn?.addEventListener("click", () => {
        quantitySpan.textContent = ++quantity;
      });

      timeInput?.addEventListener("focus", () => {
        // 기본 아이콘 안보이게, 클릭하면 편집 가능
        timeInput.type = "time";
      });
    });
  }

  // many_items_store 위치 조정
  function applyManyItemsStoreMargin() {
    if (!sheetContent) return;
    const manyItemsStores = sheetContent.querySelectorAll(".many_items_store");
    if (manyItemsStores.length === 0) return;

    const lastElement = sheetContent.lastElementChild;
    manyItemsStores.forEach((store) => {
      store.style.marginBottom = "";
    });
  }
});
