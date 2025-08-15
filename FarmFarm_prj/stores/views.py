from django.shortcuts import render, get_object_or_404, redirect
from .models import Store, StoreItem
from items.models import Item
from .forms import StoreForm, StoreItemForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

@login_required
def map_view(request):
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
                'image': store_item.photo.url if store_item.photo else '',
            })
        stores.append({
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'seller': store.seller.user.username if store.seller else '',
            'items': items,
        })

    # 판매자일 경우 가게 좌표를 context에 추가
    seller_lat = None
    seller_lng = None
    if request.user.is_authenticated and getattr(request.user, 'usertype', None) == 'SELLER':
        user_store = getattr(request.user, 'store', None)
        if user_store:
            seller_lat = user_store.latitude if user_store.latitude else 37.6509
            seller_lng = user_store.longitude if user_store.longitude else 127.0164

    context = {
        'stores': stores,
        'seller_lat': seller_lat,
        'seller_lng': seller_lng,
    }
    return render(request, 'stores/map.html', context)

def store_list(request): ##임시
    stores = Store.objects.all()
    return render(request, 'stores/store_list.html', {'stores': stores})

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
