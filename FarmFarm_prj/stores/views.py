from django.shortcuts import render, get_object_or_404, redirect
from .models import Store, StoreItem, StoreReport
from items.models import Item
from .forms import StoreForm, StoreReportForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import json
from django.views.decorators.csrf import csrf_exempt
from google.cloud import speech
import base64
import traceback
import genai
from django.conf import settings
import google.generativeai as genai
import re 


# Gemini API 키 등록 및 모델 생성
genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash-latest")

@csrf_exempt
def voice_input(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        audio_base64 = data.get("audio")
        form_type = data.get("form_type")  # 'register' 또는 'report'

        if not audio_base64:
            return JsonResponse({"error": "No audio provided"}, status=400)

        audio_bytes = base64.b64decode(audio_base64.split(",")[1])

        # Google STT
        stt_client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,  # 또는 OGG_OPUS
            language_code="ko-KR"
        )
        response = stt_client.recognize(config=config, audio=audio)
        if not response.results:
            print("Google STT 결과 없음: 오디오 형식 또는 데이터 문제")
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])

        # Gemini 호출용 prompt 생성
        if form_type == "register":
            prompt = f"""아래 문장을 판매자 가게 등록 폼 기준으로 JSON으로 만들어줘.
폼 필드:
{{'name':'', 'address':'', 'contact':'', 'sale_days':'', 'sale_hours':'', 'payment_methods':'', 'description':'', 'items':[{{'name':'', 'unit':'', 'price':'', 'description':''}}]}}
문장: {transcript}"""
        elif form_type == "report":
            prompt = f"""아래 문장을 가게 신고 폼 기준으로 JSON으로 만들어줘.
폼 필드:
{{'store_name':'', 'address':'', 'report_items':'', 'description':'', 'time':''}}
문장: {transcript}"""
        else:
            prompt = f"아래 문장을 일반 폼 JSON으로 만들어줘: {transcript}"

        # transcript 확인용 
        print("=== Transcript ===")
        print(transcript)

        # Gemini 모델로 텍스트 생성 및 구조 안전하게 파싱
        try:
            gpt_response = gemini_model.generate_content(
                prompt,
                generation_config={"max_output_tokens": 1000}
            )
            print("=== Gemini RESPONSE ===")
            print(gpt_response)  # 전체 구조 확인

            # candidates 존재 여부 체크
            if not hasattr(gpt_response, "candidates") or not gpt_response.candidates or len(gpt_response.candidates) == 0:
                raise ValueError("Gemini 반환값에 candidates가 없습니다.")

            candidate = gpt_response.candidates[0]

            # content.parts 존재 여부 체크
            if not hasattr(candidate, "content") or not hasattr(candidate.content, "parts") or not candidate.content.parts:
                raise ValueError("Gemini 후보에 content.parts가 없습니다.")

            parsed_json_text = candidate.content.parts[0].text if candidate.content.parts else None
            if parsed_json_text:
                parsed_json_text = parsed_json_text.replace("```json", "").replace("```", "").strip()
                parsed_json_text = re.sub(r'//.*', '', parsed_json_text)
                parsed_json = json.loads(parsed_json_text)
            else:
                parsed_json = {"error": "Gemini에서 데이터가 없습니다."}
                
            print("=== Gemini RAW OUTPUT ===")
            print(parsed_json_text)

        except Exception as e:
            print("Gemini 호출/파싱 에러:", e)
            parsed_json_text = None

        try:
            if parsed_json_text:  # None 체크 추가
                sanitized_text = parsed_json_text.replace("'", '"').replace('\n', '').strip()
                parsed_json = json.loads(sanitized_text)
                print("=== Gemini PARSED OUTPUT ===")
                print(parsed_json)
            else:
                parsed_json = {
                    "error": "음성에서 필요한 정보를 추출할 수 없습니다.",
                    "raw_text": transcript
                }
        except json.JSONDecodeError:
            parsed_json = {
                "error": "음성에서 필요한 정보를 추출할 수 없습니다.",
                "raw_text": parsed_json_text
            }

        return JsonResponse({"form_data": parsed_json})

    except Exception as e:
        print("에러 발생:", e)
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)
    
    
    
@login_required
def map_view(request):
    # 기존 판매자 가게
    stores_qs = Store.objects.prefetch_related('store_items', 'seller')
    stores = []
    for store in stores_qs:
        items = []
        for store_item in store.store_items.all():
            items.append({
                'id': store_item.id,
                'name': store_item.item.name,
                'price': store_item.price,
                'unit': store_item.unit,
                'description': store_item.description,
                'photo_url': store_item.photo.url if store_item.photo else ''
            })
        stores.append({
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'seller': store.seller.user.username if store.seller else '',
            'items': items
        })

    # 제보된 가게
    reports_qs = StoreReport.objects.prefetch_related('keywords', 'reporter')
    reports = []
    for report in reports_qs:
        items = []
        if report.report_items:
            for item_name in report.report_items.split(','):
                items.append({
                    'id': None,
                    'name': item_name.strip(),
                    'price': None,
                    'unit': None,
                    'description': None,
                    'photo_url': ''
                })
        keywords = [k.keyword for k in report.keywords.all()]
        reports.append({
            'id': report.id,
            'store_name': report.store_name,
            'address': report.address,
            'reporter': report.reporter.user.username,
            'items': items,
            'image': report.image.url if report.image else None,
            'keywords': keywords,
            'latitude': float(report.latitude) if report.latitude else None,
            'longitude': float(report.longitude) if report.longitude else None
        })

    # 판매자 좌표
    seller_lat = None
    seller_lng = None
    if request.user.is_authenticated and getattr(request.user, 'usertype', None) == 'SELLER':
        user_store = getattr(request.user, 'store', None)
        if user_store:
            seller_lat = user_store.latitude if user_store.latitude else 37.6509
            seller_lng = user_store.longitude if user_store.longitude else 127.0164

    context = {
        'stores': stores,
        'reports': reports,  # JS에서 바로 배열로 사용 가능
        'seller_lat': seller_lat,
        'seller_lng': seller_lng
    }

    return render(request, 'stores/map.html', context)

@login_required
def store_report(request):
    if request.method == 'POST':
        form = StoreReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user.buyer  # 신고자 연결

            # 위도/경도 안전하게 Decimal로 변환
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            try:
                report.latitude = Decimal(lat) if lat else None
            except InvalidOperation:
                report.latitude = None
            try:
                report.longitude = Decimal(lng) if lng else None
            except InvalidOperation:
                report.longitude = None

            report.save()
            form.save_m2m()  # ManyToMany 필드(키워드) 저장

            return redirect('stores:map')  
    else:
        form = StoreReportForm()

    return render(request, 'stores/store_report.html', {
        'form': form
    })
    
@login_required   
def store_list(request): ##임시
    stores = Store.objects.all()
    return render(request, 'stores/store_list.html', {'stores': stores})

@login_required
def store_detail_view(request, store_id): ##임시
    store = get_object_or_404(Store, pk=store_id)
    items = Item.objects.filter(stores=store) # 'stores' 필드 사용
    return render(request, 'stores/store_detail.html', {'store': store, 'items': items})


@login_required
def register_success(request):
    return render(request, 'stores/register_success.html')

@login_required
def register(request):
    seller = request.user.seller
    if hasattr(seller, 'store'):
        # 이미 등록된 경우 안내 페이지로 이동
        return render(request, 'stores/already_registered.html', {'store': seller.store})

    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.seller = seller
            store.business_number = seller.business_number
            store.address = request.POST.get('address', '')

            # 안전하게 Decimal 변환 + 자리 맞춤
            try:
                if request.POST.get('latitude'):
                    store.latitude = Decimal(request.POST.get('latitude')).quantize(
                        Decimal('0.000001'), rounding=ROUND_HALF_UP)
                else:
                    store.latitude = None
            except InvalidOperation:
                store.latitude = None

            try:
                if request.POST.get('longitude'):
                    store.longitude = Decimal(request.POST.get('longitude')).quantize(
                        Decimal('0.0000001'), rounding=ROUND_HALF_UP)
                else:
                    store.longitude = None
            except InvalidOperation:
                store.longitude = None

            store.save()
            form.save_m2m()

            # 품목 반복 저장
            idx = 0
            while True:
                name = request.POST.get(f'item_name_{idx}')
                price = request.POST.get(f'item_price_{idx}')
                desc = request.POST.get(f'item_desc_{idx}')
                photo = request.FILES.get(f'item_photo_{idx}')
                unit = request.POST.get(f'item_unit_{idx}')

                if not any([name, price, desc, photo]):
                    break

                if name and price:
                    item_obj, _ = Item.objects.get_or_create(name=name)
                    StoreItem.objects.create(
                        store=store,
                        item=item_obj,
                        unit=unit,
                        price=price,
                        description=desc,
                        photo=photo
                    )

                idx += 1

            seller.has_store = True
            seller.save()
            return redirect('stores:register_success')

    else:
        form = StoreForm()

    return render(request, 'stores/store_form.html', {
        'form': form,
        'store': None,
        'mode': 'register'
    })

@login_required
def edit_store(request, store_id):
    store = Store.objects.get(pk=store_id, seller=request.user.seller)

    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            # 안전하게 Decimal 변환 + 자리 맞춤
            try:
                if request.POST.get('latitude'):
                    store.latitude = Decimal(request.POST.get('latitude')).quantize(
                        Decimal('0.000001'), rounding=ROUND_HALF_UP)
                else:
                    store.latitude = None
            except InvalidOperation:
                store.latitude = None

            try:
                if request.POST.get('longitude'):
                    store.longitude = Decimal(request.POST.get('longitude')).quantize(
                        Decimal('0.0000001'), rounding=ROUND_HALF_UP)
                else:
                    store.longitude = None
            except InvalidOperation:
                store.longitude = None

            form.save()

            # 품목 반복 저장 (수정/추가)
            idx = 0
            while True:
                item_id = request.POST.get(f'item_id_{idx}')
                name = request.POST.get(f'item_name_{idx}')
                price = request.POST.get(f'item_price_{idx}')
                desc = request.POST.get(f'item_desc_{idx}')
                photo = request.FILES.get(f'item_photo_{idx}')
                unit = request.POST.get(f'item_unit_{idx}')

                if not any([name, price, desc, photo]):
                    break

                if name and price:
                    item_obj, _ = Item.objects.get_or_create(name=name)

                    if item_id:
                        # 기존 품목 수정
                        store_item = StoreItem.objects.get(pk=item_id, store=store)
                        store_item.item = item_obj
                        store_item.price = price
                        store_item.description = desc
                        store_item.unit = unit
                        if photo:
                            store_item.photo = photo
                        store_item.save()
                    else:
                        # 새 품목 추가
                        StoreItem.objects.create(
                            store=store,
                            item=item_obj,
                            unit=unit,
                            price=price,
                            description=desc,
                            photo=photo
                        )

                idx += 1

            return redirect('users:seller_home')

    else:
        form = StoreForm(instance=store)

    return render(request, 'stores/store_form.html', {
        'form': form,
        'store': store,
        'mode': 'edit'
    })

@login_required
def edit_item(request, item_id):
    store_item = StoreItem.objects.get(pk=item_id, store__seller=request.user.seller)
    if request.method == 'POST':
        name = request.POST.get('item_name')
        price = request.POST.get('item_price')
        desc = request.POST.get('item_desc')
        photo = request.FILES.get('item_photo')
        unit = request.POST.get('item_unit')  # 단위 값 받기
        item_obj, _ = Item.objects.get_or_create(name=name)
        store_item.item = item_obj
        store_item.price = price
        store_item.description = desc
        store_item.unit = unit  # 단위 저장
        if photo:
            store_item.photo = photo
        store_item.save()
        return redirect('users:seller_home')
    return render(request, 'stores/edit_item.html', {
        'store_item': store_item
    })


