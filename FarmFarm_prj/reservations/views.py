# reservations/views.py
import json
from typing import Any, Dict, List

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_datetime
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import (
    Reservation,
    ReservationItem,
    ReservationStatus,
    RejectReason,
)

# ---------- 유틸 ----------
def _json_body(request) -> Dict[str, Any] | None:
    ctype = request.META.get("CONTENT_TYPE", "")
    if "application/json" in ctype:
        try:
            return json.loads(request.body.decode("utf-8"))
        except Exception:
            return None
    return None

def _badge_text(r: Reservation) -> str:
    if r.status == ReservationStatus.PICKED_UP:
        return "픽업 완료"
    if r.status == ReservationStatus.READY:
        return "픽업 가능"
    if r.status in (ReservationStatus.ACCEPTED, ReservationStatus.PREPARING):
        return f"{r.prep_eta_minutes}분 후 픽업 가능" if r.prep_eta_minutes else "준비중"
    if r.status == ReservationStatus.PENDING:
        return "승인 대기"
    if r.status == ReservationStatus.REJECTED:
        return "거절됨"
    if r.status == ReservationStatus.CANCELLED:
        return "취소됨"
    return "예약"

def _reservation_to_dict(r: Reservation) -> Dict[str, Any]:
    return {
        "id": r.id,
        "store_id": r.store_id,
        "store_name": getattr(r.store, "name", None),
        "buyer_id": r.buyer_id,
        "buyer_name": getattr(getattr(r.buyer, "user", None), "username", None),
        "requested_pickup_at": r.requested_pickup_at.isoformat(),
        "note": r.note,
        "status": r.status,
        "status_label": r.get_status_display(),
        "rejected_reason": r.rejected_reason or "",
        "rejected_reason_label": dict(RejectReason.choices).get(r.rejected_reason, "") if r.rejected_reason else "",
        "rejected_reason_detail": r.rejected_reason_detail,
        "cancelled_reason": r.cancelled_reason,
        "accepted_at": r.accepted_at.isoformat() if r.accepted_at else None,
        "prepared_at": r.prepared_at.isoformat() if r.prepared_at else None,
        "ready_at": r.ready_at.isoformat() if r.ready_at else None,
        "picked_up_at": r.picked_up_at.isoformat() if r.picked_up_at else None,
        "cancelled_at": r.cancelled_at.isoformat() if r.cancelled_at else None,
        "rejected_at": r.rejected_at.isoformat() if r.rejected_at else None,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "total_price": r.total_price,
        "contact_phone": r.contact_phone,
        "display_image_url": r.display_image.url if r.display_image else "",
        "reservation_code": r.reservation_code,
        "seller_note": r.seller_note,
        "prep_eta_minutes": r.prep_eta_minutes,
        "pickup_window_start": r.pickup_window_start.isoformat() if r.pickup_window_start else None,
        "pickup_window_end": r.pickup_window_end.isoformat() if r.pickup_window_end else None,
        "badge_text": _badge_text(r),
        "items": [
            {
                "id": it.id,
                "item_name": it.item_name,
                "unit_price": it.unit_price,
                "quantity": it.quantity,
                "unit": it.unit,
                "memo": it.memo,
                "image_url": it.image.url if it.image else "",
                "line_total": it.unit_price * it.quantity,
            }
            for it in r.items.all()
        ],
    }

def _parse_items_from_json(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    parsed: List[Dict[str, Any]] = []
    for it in items:
        parsed.append(
            {
                "item_name": str(it.get("item_name", "")).strip(),
                "unit_price": int(it.get("unit_price", 0)),
                "quantity": int(it.get("quantity", 1)),
                "unit": str(it.get("unit", "")).strip(),
                "memo": str(it.get("memo", "")).strip(),
            }
        )
    return parsed

# ---------- 페이지 렌더 ----------
def page_buyer_reservations(request):
    buyer_id = int(request.GET.get("buyer", "1"))
    return render(request, "reservations/buyer_list.html", {"buyer_id": buyer_id})

def page_seller_reservations(request):
    store_id = int(request.GET.get("store", "1"))
    return render(request, "reservations/seller_list.html", {"store_id": store_id})

# ---------- JSON: 생성/조회 ----------
@require_http_methods(["POST"])
def reservation_create(request):
    data = _json_body(request) or request.POST

    store_id = data.get("store_id")
    buyer_id = data.get("buyer_id")
    requested_pickup_at = data.get("requested_pickup_at")

    if not (store_id and buyer_id and requested_pickup_at):
        return HttpResponseBadRequest("store_id, buyer_id, requested_pickup_at는 필수입니다.")

    dt = parse_datetime(str(requested_pickup_at))
    if not dt:
        return HttpResponseBadRequest("requested_pickup_at 형식이 올바르지 않습니다. (ISO-8601)")

    display_image = request.FILES.get("display_image") if hasattr(request, "FILES") else None

    r = Reservation.objects.create(
        store_id=int(store_id),
        buyer_id=int(buyer_id),
        requested_pickup_at=dt,
        note=str(data.get("note", "")),
        contact_phone=str(data.get("contact_phone", "")),
        display_image=display_image or None,
    )

    items = []
    if isinstance(data, dict) and "items" in data:
        try:
            items = _parse_items_from_json(data.get("items") or [])
        except Exception:
            return HttpResponseBadRequest("items 파싱에 실패했습니다.")

    for it in items:
        ReservationItem.objects.create(reservation=r, **it)

    r.refresh_from_db()
    return JsonResponse(_reservation_to_dict(r), status=201, json_dumps_params={"ensure_ascii": False})

@require_http_methods(["GET"])
def reservation_detail(request, pk: int):
    r = get_object_or_404(Reservation.objects.prefetch_related("items", "store", "buyer__user"), pk=pk)
    return JsonResponse(_reservation_to_dict(r), json_dumps_params={"ensure_ascii": False})

@require_http_methods(["GET"])
def reservation_list_by_buyer(request, buyer_id: int):
    qs = (
        Reservation.objects.filter(buyer_id=buyer_id)
        .select_related("store", "buyer__user")
        .prefetch_related("items")
        .order_by("-created_at")
    )
    data = [_reservation_to_dict(r) for r in qs]
    return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False})

@require_http_methods(["GET"])
def reservation_list_by_store(request, store_id: int):
    status_filter = request.GET.get("status")
    qs = Reservation.objects.filter(store_id=store_id)
    if status_filter:
        qs = qs.filter(status=status_filter)
    qs = qs.select_related("store", "buyer__user").prefetch_related("items").order_by("-created_at")
    data = [_reservation_to_dict(r) for r in qs]
    return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False})

# ---------- JSON: 상태 변경 ----------
@require_http_methods(["POST"])
def reservation_accept(request, pk: int):
    r = get_object_or_404(Reservation, pk=pk)
    r.status = ReservationStatus.ACCEPTED
    r.accepted_at = timezone.now()
    r.save(update_fields=["status", "accepted_at"])
    return JsonResponse(_reservation_to_dict(r), json_dumps_params={"ensure_ascii": False})

@require_http_methods(["POST"])
def reservation_reject(request, pk: int):
    r = get_object_or_404(Reservation, pk=pk)
    data = _json_body(request) or request.POST
    reason = data.get("reason", RejectReason.OTHER)
    detail = data.get("detail", "")
    r.status = ReservationStatus.REJECTED
    r.rejected_reason = reason
    r.rejected_reason_detail = detail
    r.rejected_at = timezone.now()   # <- 오타 주의!
    r.save(update_fields=["status", "rejected_reason", "rejected_reason_detail", "rejected_at"])
    return JsonResponse(_reservation_to_dict(r), json_dumps_params={"ensure_ascii": False})

@require_http_methods(["POST"])
def reservation_ready(request, pk: int):
    r = get_object_or_404(Reservation, pk=pk)
    r.status = ReservationStatus.READY
    r.ready_at = timezone.now()
    r.save(update_fields=["status", "ready_at"])
    return JsonResponse(_reservation_to_dict(r), json_dumps_params={"ensure_ascii": False})

@require_http_methods(["POST"])
def reservation_picked_up(request, pk: int):
    r = get_object_or_404(Reservation, pk=pk)
    r.status = ReservationStatus.PICKED_UP
    r.picked_up_at = timezone.now()
    r.save(update_fields=["status", "picked_up_at"])
    return JsonResponse(_reservation_to_dict(r), json_dumps_params={"ensure_ascii": False})

@require_http_methods(["POST"])
def reservation_cancel(request, pk: int):
    r = get_object_or_404(Reservation, pk=pk)
    data = _json_body(request) or request.POST
    reason = str(data.get("reason", ""))
    r.status = ReservationStatus.CANCELLED
    r.cancelled_reason = reason
    r.cancelled_at = timezone.now()
    r.save(update_fields=["status", "cancelled_reason", "cancelled_at"])
    return JsonResponse(_reservation_to_dict(r), json_dumps_params={"ensure_ascii": False})

@require_http_methods(["POST"])
def reservation_update_meta(request, pk: int):
    r = get_object_or_404(Reservation, pk=pk)
    data = _json_body(request) or request.POST

    if "prep_eta_minutes" in data:
        try:
            r.prep_eta_minutes = max(0, int(data.get("prep_eta_minutes", 0)))
        except ValueError:
            return HttpResponseBadRequest("prep_eta_minutes는 정수여야 합니다.")

    if "seller_note" in data:
        r.seller_note = str(data.get("seller_note") or "")

    if hasattr(request, "FILES") and request.FILES.get("display_image"):
        r.display_image = request.FILES["display_image"]

    r.save()
    return JsonResponse(_reservation_to_dict(r), json_dumps_params={"ensure_ascii": False})
