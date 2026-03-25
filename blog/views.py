import json
from datetime import date

from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Campaign, Post


def post_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def _parse_iso_date(value):
    if value is None or value == '':
        return None
    if not isinstance(value, str):
        raise ValueError('date must be a string in YYYY-MM-DD format')
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError('date must be in YYYY-MM-DD format') from exc


def _bad_request(message, fields=None):
    payload = {'error': message}
    if fields:
        payload['fields'] = fields
    return JsonResponse(payload, status=400)


@csrf_exempt
@require_POST
def create_campaign(request):
    """
    Create a communication campaign via JSON.

    Security note: view is csrf_exempt for simplicity. In production,
    add authentication/authorization and proper CSRF/CORS strategy.
    """
    try:
        raw = request.body.decode('utf-8')
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return _bad_request('Invalid JSON body')

    name = data.get('name')
    if not isinstance(name, str) or not name.strip():
        return _bad_request('Missing or invalid field: name', {'name': 'required'})

    description = data.get('description', '')
    if description is not None and not isinstance(description, str):
        return _bad_request('Invalid field: description', {'description': 'must be a string'})

    objective = data.get('objective', '')
    if objective is not None and not isinstance(objective, str):
        return _bad_request('Invalid field: objective', {'objective': 'must be a string'})

    channels = data.get('channels', [])
    if channels is None:
        channels = []
    if not isinstance(channels, list) or not all(isinstance(c, str) for c in channels):
        return _bad_request('Invalid field: channels', {'channels': 'must be a list of strings'})

    status = data.get('status', Campaign.Status.DRAFT)
    if not isinstance(status, str):
        return _bad_request('Invalid field: status', {'status': 'must be a string'})
    valid_statuses = {choice[0] for choice in Campaign.Status.choices}
    if status not in valid_statuses:
        return _bad_request('Invalid field: status', {'status': f'must be one of {sorted(valid_statuses)}'})

    try:
        start_date = _parse_iso_date(data.get('start_date'))
        end_date = _parse_iso_date(data.get('end_date'))
    except ValueError as exc:
        return _bad_request(str(exc))

    budget = data.get('budget')
    if budget in ('', None):
        budget = None

    else:
        try:
            budget = str(budget)
        except Exception:
            return _bad_request('Invalid field: budget', {'budget': 'must be a number'})

    try:
        campaign = Campaign(
            name=name.strip(),
            description=description or '',
            objective=objective or '',
            channels=channels,
            status=status,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
        )
        # Enforce model-level validation (e.g., date ordering).
        campaign.full_clean()
        campaign.save()
    except ValidationError as exc:
        detail = getattr(exc, 'message_dict', None) or {'detail': exc.messages}
        return _bad_request('Validation error', detail)

    return JsonResponse(
        {
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'objective': campaign.objective,
            'channels': campaign.channels,
            'budget': str(campaign.budget) if campaign.budget is not None else None,
            'status': campaign.status,
            'start_date': campaign.start_date.isoformat() if campaign.start_date else None,
            'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
            'created_at': campaign.created_at.isoformat(),
        },
        status=201,
    )
