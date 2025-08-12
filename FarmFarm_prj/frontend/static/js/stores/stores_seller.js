document.addEventListener("DOMContentLoaded", function () {
  // kakao 객체 있는지 체크 후 지도 로딩
  if (typeof kakao !== "undefined" && kakao.maps) {
    const container = document.getElementById("map");
    const options = {
      center: new kakao.maps.LatLng(37.5665, 126.978),
      level: 3,
    };
    const map = new kakao.maps.Map(container, options);

    const ps = new kakao.maps.services.Places();
    let marker = new kakao.maps.Marker();

    // 검색 버튼 이벤트
    document
      .getElementById("searchBtn")
      .addEventListener("click", searchPlaces);
    document.getElementById("searchInput").addEventListener("keypress", (e) => {
      if (e.key === "Enter") searchPlaces();
    });

    function searchPlaces() {
      const keyword = document.getElementById("searchInput").value.trim();
      if (!keyword) {
        alert("검색어를 입력하세요!");
        return;
      }
      ps.keywordSearch(keyword, placesSearchCB);
    }

    function placesSearchCB(data, status) {
      if (status === kakao.maps.services.Status.OK) {
        const place = data[0];
        const coords = new kakao.maps.LatLng(place.y, place.x);

        map.setCenter(coords);
        marker.setMap(null);
        marker = new kakao.maps.Marker({ position: coords });
        marker.setMap(map);
      } else {
        alert("검색 결과가 없습니다.");
      }
    }
  } else {
    // 지도 로딩 실패 시 안내 문구만 표시
    document.getElementById("errorMessage").innerHTML =
      "카카오맵을 불러올 수 없습니다.<br>API 키를 확인해주세요.";
  }


  const testBtn = document.getElementById("test");
  const bottomSheet = document.getElementById("bottomSheet");

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

  const sheetContent = document.querySelector(".sheet_content_v2");

  let lastScrollTop = 0;
  let isExpanded = false;

  sheetContent.addEventListener("scroll", () => {
    const currentScrollTop = sheetContent.scrollTop;

    if (currentScrollTop > lastScrollTop) {
      // 아래로 스크롤 중
      if (!isExpanded) {
        bottomSheet.classList.add("expanded");
        isExpanded = true;
      }
    } else {
      // 위로 스크롤 중
      if (isExpanded) {
        bottomSheet.classList.remove("expanded");
        isExpanded = false;
      }
    }

    lastScrollTop = currentScrollTop <= 0 ? 0 : currentScrollTop;
  });

  function hideBottomSheet() {
    bottomSheet.classList.remove("show", "expanded");
    bottomSheet.classList.add("hidden");
  }
  testBtn.addEventListener("click", () => {
    bottomSheet.classList.remove("hidden");
    bottomSheet.classList.add("show");
  });
});
