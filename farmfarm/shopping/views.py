# shopping/views.py

import google.generativeai as genai
from collections import defaultdict

from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.db.models import Q
from geopy.distance import geodesic

from stores.models import Store, StoreItem # Product 모델 대신 StoreItem을 사용

class AiShoppingView(View):
    def get(self, request, *args, **kwargs):
        """
        GET 요청 시에는 사용자가 요리 이름을 입력할 초기 검색폼을 보여줍니다.
        """
        return render(request, 'shopping/ai_search.html')

    def post(self, request, *args, **kwargs):
        """
        POST 요청 시에는 AI 분석 후, 결과를 지도와 함께 보여줄 ai_results.html을 렌더링합니다.
        """
        dish_name = request.POST.get('dish', '').strip()

        if not dish_name:
            return render(request, 'shopping/ai_search.html', {'error': '음식 이름을 입력해주세요.'})
        
        # --- 1. Gemini API를 사용하여 재료 분석 ---
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            prompt = (
                f"'{dish_name}' 요리를 만드는데 필요한 핵심 재료들을 쉼표(,)로만 구분된 목록으로 알려줘. "
                f"예를 들어 '쌀,계란,콩나물,시금치' 처럼 다른 설명 없이 재료 이름만 나열해줘."
            )
            response = model.generate_content(prompt)
            ingredients_text = response.text
            ingredient_names = [name.strip() for name in ingredients_text.split(',') if name.strip()]
            print("\n" + "="*50)
            print(f"[AI 응답] 추천 재료: {ingredient_names}")
            print("="*50)
        except Exception as e:
            print(f"AI API Error: {e}")
            return render(request, 'shopping/ai_error.html', {'error_message': 'AI 서버와 통신 중 오류가 발생했습니다.'})

        # --- 2. 분석된 재료 "이름을 포함하는" 가게 상품 검색 ---
        user_location = (37.638, 127.025) # 데모용 고정 위치 (수유역 근처)
        stores_data = defaultdict(lambda: {'info': None, 'products': [], 'distance': 0})
        
        if ingredient_names:
            query = Q()
            for name in ingredient_names:
                query |= Q(item__name__icontains=name)

            found_store_items = StoreItem.objects.filter(query).select_related('store', 'item')
        else:
            found_store_items = StoreItem.objects.none()
        print("="*50)
        print("[DB 조회 결과] 아래 가게/상품들을 찾았습니다:")
        if not found_store_items:
            print(" >> 찾은 상품 없음")
        for item in found_store_items:
            print(f" >> 가게: {item.store.name}, 상품: {item.item.name}")
        print("="*50 + "\n")

        for store_item in found_store_items:
            store = store_item.store
            store_id = store.id
            
            if not stores_data[store_id]['info']:
                stores_data[store_id]['info'] = store
                if store.latitude and store.longitude:
                    store_location = (store.latitude, store.longitude)
                    distance = geodesic(user_location, store_location).km
                    stores_data[store_id]['distance'] = round(distance, 2)
        
        # --- 3. 템플릿에 전달할 context 데이터 가공 ---
        sorted_stores_list = sorted(stores_data.values(), key=lambda item: item['distance'])
        
        stores_for_map = []
        for store_data in sorted_stores_list:
            if store_data['info'].latitude and store_data['info'].longitude:
                stores_for_map.append({
                    'id': store_data['info'].id,
                    'name': store_data['info'].name,
                    'latitude': float(store_data['info'].latitude),
                    'longitude': float(store_data['info'].longitude),
                    'distance': store_data['distance'],
                })

        context = {
            'dish_name': dish_name,
            'ingredient_names': ingredient_names,
            'stores_for_map_json': stores_for_map,
            'user_location': { 'lat': user_location[0], 'lng': user_location[1] }
        }
        return render(request, 'shopping/ai_results.html', context)