document.addEventListener("DOMContentLoaded", function () {
  window.handleBoxImageUpload = function (event, index) {
    const file = event.target.files[0];
    const label = event.target.closest(".image-box");
    const img = label.querySelector("img.preview-img");
    const plus = label.querySelector(".plus-icon");

    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
      img.src = e.target.result;
      img.style.display = "block";
      plus.style.display = "none";
    };
    reader.readAsDataURL(file);
  };

  window.toggleFood = function (el) {
    el.classList.toggle("selected");
  };

  const foodInput = document.querySelector(".food-input");
  const addBtn = document.querySelector(".add-food-btn");
  const foodList = document.querySelector(".food-list");

  window.showFoodInput = function () {
    foodInput.style.display = "inline-block";
    foodInput.focus();
  };

  function addFood(name) {
    const newFood = document.createElement("div");
    newFood.className = "food-option";
    newFood.textContent = name;
    newFood.onclick = () => window.toggleFood(newFood);
    foodList.insertBefore(newFood, addBtn);
  }

  foodInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      const value = foodInput.value.trim();
      if (value !== "") {
        addFood(value);
        foodInput.value = "";
        foodInput.style.display = "none";
      }
    }
  });

  foodInput.addEventListener("blur", function () {
    const value = foodInput.value.trim();
    if (value !== "") {
      addFood(value);
    }
    foodInput.value = "";
    foodInput.style.display = "none";
  });
  window.addNewFood = function () {
    const foodList = document.querySelector(".food-list");
    const addBtn = document.querySelector(".add-food-btn");

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "입력";
    input.className = "food-option-input";

    if (document.querySelector(".food-option-input")) return;

    foodList.insertBefore(input, addBtn);
    input.focus();

    const finalize = () => {
      const newName = input.value.trim();
      if (newName !== "") {
        const newFood = document.createElement("div");
        newFood.className = "food-option";
        newFood.textContent = newName;
        newFood.onclick = () => window.toggleFood(newFood);
        foodList.insertBefore(newFood, input);
      }
      input.remove();
    };

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        finalize();
      }
    });

    input.addEventListener("blur", () => {
      finalize();
    });
  };
  
  document.getElementById("storeForm").addEventListener("submit", function (e) {
    const selectedFoods = [];
    document
      .querySelectorAll("#foodList .food-option.selected")
      .forEach((el) => {
        selectedFoods.push(el.textContent.trim());
      });
    document.getElementById("selectedFoodsInput").value =
      JSON.stringify(selectedFoods);

    const selectedKeywords = [];
    document
      .querySelectorAll("#keywordList .food-option.selected")
      .forEach((el) => {
        selectedKeywords.push(el.textContent.trim());
      });
    document.getElementById("selectedKeywordsInput").value =
      JSON.stringify(selectedKeywords);
  });
  

});
