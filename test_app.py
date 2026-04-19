import pytest

def test_always_passes():
    assert True == True

def test_app_imports():
    # Проверяем, что app.py можно импортировать
    import sys
    sys.path.append('.')
    import app
    assert hasattr(app, 'app')