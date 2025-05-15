import json
import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from app.views import IndexView

@pytest.fixture
def rf():
    return RequestFactory()

@pytest.fixture
def user(django_user_model):
    """Create a simple user for authentication."""
    return django_user_model.objects.create_user(username='testuser', password='password')

@pytest.fixture(autouse=True)
def stub_movie_and_history(monkeypatch):
    """
    Stub out get_movie_datas() and get_history() so they return predictable data.
    """
    mock_images = ['img1.jpg', 'img2.jpg']
    mock_titles = ['Title 1', 'Title 2']
    mock_synopses = ['Synopsis 1', 'Synopsis 2']
    mock_urls = ['/url1', '/url2']
    mock_predictions = {'foo': 'bar'}
    monkeypatch.setattr(
        'app.views.get_movie_datas',
        lambda: (mock_images, mock_titles, mock_synopses, mock_urls, mock_predictions)
    )
    mock_history = [
        {'date': '2025-05-01', 'action': 'watched'},
        {'date': '2025-05-02', 'action': 'predicted'},
    ]
    monkeypatch.setattr('app.views.get_history', lambda: mock_history)

def test_get_context_data_default(rf, user):
    """
    Logged-in user with no content= param should get all base context keys
    and no flags set.
    """
    request = rf.get('/index/')  # URL doesn't matter since we're calling the view directly
    request.user = user

    view = IndexView()
    view.setup(request)

    context = view.get_context_data()

    # movie_list is zipped from the four lists
    expected_movie_list = list(zip(
        ['img1.jpg', 'img2.jpg'],
        ['Title 1', 'Title 2'],
        ['Synopsis 1', 'Synopsis 2'],
        ['/url1', '/url2'],
    ))
    assert context['movie_list'] == expected_movie_list

    # predictions and history come through untouched
    assert context['predictions'] == {'foo': 'bar'}
    assert context['history'] == [
        {'date': '2025-05-01', 'action': 'watched'},
        {'date': '2025-05-02', 'action': 'predicted'},
    ]

    # figures list should be exactly fig1.png … fig12.png
    assert context['figures'] == [f'fig{i}.png' for i in range(1, 13)]

    # history_json must be valid JSON string of the history list
    assert json.loads(context['history_json']) == context['history']

    # no tab-specific flags by default
    for flag in ('is_releases', 'is_predictions', 'is_dashboard', 'is_history'):
        assert flag not in context, f"{flag} should not be in context by default"

@pytest.mark.parametrize('tab,flag', [
    ('releases',    'is_releases'),
    ('predictions', 'is_predictions'),
    ('dashboard',   'is_dashboard'),
    ('history',     'is_history'),
])
def test_content_flags(rf, user, tab, flag):
    """
    When ?content=<tab> is in the querystring, the corresponding
    is_<tab> flag must be set to True.
    """
    request = rf.get(f'/index/?content={tab}')
    request.user = user

    view = IndexView()
    view.setup(request)
    context = view.get_context_data()

    # Only the one flag should be True; others absent
    assert context.get(flag) is True
    for other in ('is_releases', 'is_predictions', 'is_dashboard', 'is_history'):
        if other != flag:
            assert other not in context

def test_login_required_redirect(rf):
    """
    Anonymous user should be redirected (302) by the LoginRequiredMixin.
    """
    request = rf.get('/index/')
    request.user = AnonymousUser()

    view = IndexView()
    view.setup(request)
    response = view.dispatch(request)

    assert response.status_code == 302
