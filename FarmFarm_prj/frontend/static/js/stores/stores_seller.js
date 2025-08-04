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

  testBtn.addEventListener("click", () => {
    bottomSheet.classList.remove("hidden");
    bottomSheet.classList.add("show");
  });
});
