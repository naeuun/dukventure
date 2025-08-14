from django.shortcuts import render, get_object_or_404
from .models import Store
from items.models import Item

# Create your views here.
def map_view(request):
    # 나중에 지도에 표시할 가게 데이터를 여기서 전달할 수 있습니다.
    # stores = Store.objects.all()
    # context = {'stores': stores}
    return render(request, 'stores/map.html') # 올바른 템플릿 경로



def store_list_view(request): ##임시
    stores = Store.objects.all()
    return render(request, 'stores/store_list.html', {'stores': stores})

def store_detail_view(request, store_id): ##임시
    store = get_object_or_404(Store, pk=store_id)
    items = Item.objects.filter(stores=store) # 'stores' 필드 사용
    return render(request, 'stores/store_detail.html', {'store': store, 'items': items})
