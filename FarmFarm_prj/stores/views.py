from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import StoreForm, StoreItemForm
from django.contrib.auth.decorators import login_required
from items.models import Item
from .models import StoreItem, Store

def map(request):
    stores_qs = Store.objects.all()
    stores = []
    for store in stores_qs:
        if store.address:
            stores.append({
                'name': store.name,
                'address': store.address,
                'seller': getattr(store.seller, 'name', getattr(store.seller.user, 'username', ''))
            })
    return render(request, 'stores/map.html', {'stores': stores})    

@login_required
def register_success(request):
    return render(request, 'stores/register_success.html')

@login_required
def register(request):
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.seller = request.user.seller
            store.business_number = request.user.seller.business_number
            store.address = request.POST.get('address', '')
            store.save()
            form.save_m2m()
            # 품목 반복적으로 저장
            idx = 0
            while True:
                name = request.POST.get(f'item_name_{idx}')
                price = request.POST.get(f'item_price_{idx}')
                desc = request.POST.get(f'item_desc_{idx}')
                photo = request.FILES.get(f'item_photo_{idx}')
                # 모든 값이 None이면 반복 종료
                if name is None and price is None and desc is None and photo is None:
                    break
                # name과 price가 있으면 저장
                if name and price:
                    item_obj, _ = Item.objects.get_or_create(name=name)
                    StoreItem.objects.create(
                        store=store,
                        item=item_obj,
                        price=price,
                        description=desc,
                        photo=photo
                    )
                idx += 1
            seller = request.user.seller
            seller.has_store = True
            seller.save()
            return redirect('stores:register_success')
    else:
        form = StoreForm()
    return render(request, 'stores/register.html', {'form': form})