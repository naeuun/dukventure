# shopping/views.py

import google.generativeai as genai
from collections import defaultdict

from django.conf import settings
from django.shortcuts import render
from django.views import View
from geopy.distance import geodesic

from .models import Product, Ingredient
from stores.models import Store # 실제 프로젝트의 Store 모델 경로에 맞게 수정

class AiShoppingView(View):
    """
    AI 기반 장보기 코스 추천 뷰
    GET: 요리 이름 입력 폼을 보여주는 페이지
    POST: 입력된 요리를 분석하여 재료를 판매하는 가게 목록을 결과 페이지에 표시
    """
    
    def get(self, request, *args, **kwargs):
        # GET 요청 시에는 사용자가 요리 이름을 입력할 폼을 보여줍니다.
        return render(request, 'shopping/ai_search.html')

    def post(self, request, *args, **kwargs):
        dish_name = request.POST.get('dish', '').strip()

        if not dish_name:
            # 입력값이 없을 경우, 에러 메시지와 함께 다시 검색폼을 보여줍니다.
            return render(request, 'shopping/ai_search.html', {'error': '음식 이름을 입력해주세요.'})
        
        # --- 1. Gemini API를 사용하여 재료 분석 ---
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # AI에게 원하는 결과 형식을 명확하게 지시하는 것이 중요합니다.
            prompt = (
                f"'{dish_name}' 요리를 만드는데 필요한 핵심 재료들을 쉼표(,)로만 구분된 목록으로 알려줘. "
                f"예를 들어 '쌀,계란,콩나물,시금치' 처럼 다른 설명 없이 재료 이름만 나열해줘."
            )
            
            response = model.generate_content(prompt)
            ingredients_text = response.text
            
            # AI 응답 파싱: "계란, 콩나물, 돼지고기" -> ['계란', '콩나물', '돼지고기']
            ingredient_names = [name.strip() for name in ingredients_text.split(',') if name.strip()]

              # --- AI 대답 확인용도(임시) ---
            print("="*50)
            print(f"방금 AI에게 물어본 요리: {dish_name}")
            print(f"AI가 실제로 대답한 재료 목록: {ingredient_names}")
            print("="*50)
            # --- 여기까지 추가 ---
            
        except Exception as e:
            # API 호출 실패 또는 다른 예외 발생 시 에러 페이지를 보여줍니다.
            print(f"AI API Error: {e}")
            # 실제 서비스에서는 로깅(logging) 처리를 하는 것이 좋습니다.
            return render(request, 'shopping/ai_error.html', {'error_message': 'AI 서버와 통신 중 오류가 발생했습니다.'})

        # --- 2. 분석된 재료를 판매하는 가게 검색 ---
        # 사용자 위치 (데모용 - 서울 시청 기준)
        # 실제 서비스에서는 로그인한 유저의 주소나 GPS 정보를 사용해야 합니다.
        user_location = (37.5665, 126.9780)
        
        # `defaultdict`를 사용하여 가게별로 상품을 편리하게 그룹화합니다.
        # stores_data = { store_id: {'info': store_object, 'products': [product1, product2], 'distance': 1.2}, ... }
        stores_data = defaultdict(lambda: {'info': None, 'products': [], 'distance': 0})
        
        # `ingredient__name__in`을 사용하여 분석된 모든 재료를 한 번의 쿼리로 조회합니다.
        # `select_related`는 정참조 ForeignKey 필드를 미리 JOIN하여 DB 접근 횟수를 줄여줍니다. (성능 최적화)
        found_products = Product.objects.filter(
            ingredient__name__in=ingredient_names,
            is_available=True
        ).select_related('store', 'ingredient')

        for product in found_products:
            store = product.store
            store_id = store.id
            
            # 아직 가게 정보가 기록되지 않았다면, 가게 정보와 거리를 계산하여 저장
            if not stores_data[store_id]['info']:
                stores_data[store_id]['info'] = store
                if store.latitude and store.longitude:
                    store_location = (store.latitude, store.longitude)
                    distance = geodesic(user_location, store_location).km
                    stores_data[store_id]['distance'] = round(distance, 2) # 소수점 2자리까지 반올림
            
            # 해당 가게에 찾은 상품 추가
            stores_data[store_id]['products'].append(product)

        # --- 3. 가게를 거리순으로 정렬 ---
        if not stores_data:
            # 재료를 파는 가게가 없을 경우
            context = {
                'dish_name': dish_name,
                'ingredient_names': ingredient_names,
                'stores_list': []
            }
            return render(request, 'shopping/ai_results.html', context)

        # 거리(distance)를 기준으로 오름차순 정렬
        sorted_stores_list = sorted(stores_data.values(), key=lambda item: item['distance'])
        
        context = {
            'dish_name': dish_name,
            'ingredient_names': ingredient_names,
            'stores_list': sorted_stores_list,
        }

        return render(request, 'shopping/ai_results.html', context)