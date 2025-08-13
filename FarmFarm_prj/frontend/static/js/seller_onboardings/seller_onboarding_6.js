document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("verify");
  const text = document.getElementById("text");
  let cnt = 0;

  btn.addEventListener("click", function () {
    cnt++;

    if (cnt === 1) {
      text.innerHTML = "인증완료";
    } else if (cnt === 2) {
      location.href = "selleronboarding5";
    }
  });
});
