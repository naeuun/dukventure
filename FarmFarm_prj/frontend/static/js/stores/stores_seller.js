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

    // 기본 마커 이미지 (필요하면 변경)
    const imageSize = new kakao.maps.Size(20, 20);
    const imageOption = { offset: new kakao.maps.Point(20, 40) };
    const markerImageSrc = "/static/img/stores.png"; // 마커 이미지 경로 설정
    const markerImage = new kakao.maps.MarkerImage(
      markerImageSrc,
      imageSize,
      imageOption
    );

    // 샘플 가게들
    const stores = [
      {
        name: "4.19민주역 달걀 할머니",
        lat: 37.6495,
        lng: 127.0141,
      },
      {
        name: "4.19민주역 달걀 할머니",
        lat: 37.6495,
        lng: 127.0151,
      },
    ];

    // 가게별 마커 생성 및 클릭 이벤트에 바텀시트 열기 추가
    stores.forEach((store) => {
      const position = new kakao.maps.LatLng(store.lat, store.lng);
      const storeMarker = new kakao.maps.Marker({
        map: map,
        position: position,
        title: store.name,
        image: markerImage,
      });

      kakao.maps.event.addListener(storeMarker, "click", () => {
        openBottomSheet();
        // 필요하면 바텀시트 내 정보 갱신 코드 추가 가능
      });
    });

    // 검색 버튼 및 엔터키로 장소 검색
    const ps = new kakao.maps.services.Places();
    searchBtn.addEventListener("click", searchPlaces);
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") searchPlaces();
    });
function searchPlaces() {
  const keyword = searchInput.value.trim();
  if (!keyword) {
    alert("검색어를 입력하세요!");
    return;
  }

  // stores 중 이름에 keyword 포함하는 가게만 필터링
  const filteredStores = stores.filter((store) => store.name.includes(keyword));

  if (filteredStores.length === 0) {
    alert("검색 결과가 없습니다.");
    return;
  }

  // 기존 검색 마커 제거
  if (marker) {
    marker.setMap(null);
  }

  // 만약 여러 개면 첫 번째 가게 위치로 지도 이동하고 마커 표시
  const firstStore = filteredStores[0];
  const coords = new kakao.maps.LatLng(firstStore.lat, firstStore.lng);
  map.setCenter(coords);

  marker = new kakao.maps.Marker({
    position: coords,
    map: map,
    title: firstStore.name,
  });

  // 마커 클릭 시 바텀시트 열기
  kakao.maps.event.addListener(marker, "click", () => {
    openBottomSheet();
  });
}


    function placesSearchCB(data, status) {
      if (status === kakao.maps.services.Status.OK) {
        const place = data[0];
        const coords = new kakao.maps.LatLng(place.y, place.x);

        map.setCenter(coords);

        // 기존 검색 마커 제거 후 새로 표시
        if (marker) {
          marker.setMap(null);
        }
        marker = new kakao.maps.Marker({
          position: coords,
          map: map,
          title: place.place_name,
        });

        // 마커 클릭 시 바텀시트 열기 (필요시)
        kakao.maps.event.addListener(marker, "click", () => {
          openBottomSheet();
        });
      } else {
        alert("검색 결과가 없습니다.");
      }
    }
  } else {
    document.getElementById("errorMessage").innerHTML =
      "카카오맵을 불러올 수 없습니다.<br>API 키를 확인해주세요.";
  }

  // 바텀시트 열기/닫기 함수
  function openBottomSheet() {
    bottomSheet.classList.remove("hidden");
    bottomSheet.classList.add("show");
  }
  function hideBottomSheet() {
    bottomSheet.classList.remove("show", "expanded");
    bottomSheet.classList.add("hidden");
  }

  // 바텀시트 터치 드래그 이벤트
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

  // 바텀시트 내 스크롤 이벤트 (확장/축소 제어)
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

  // 지도 클릭 시 바텀시트 닫기
  container.addEventListener("click", () => {
    hideBottomSheet();
  });

});
