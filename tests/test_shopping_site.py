import pytest
from shopping_site import app
from flask import Flask, session, request, redirect, url_for

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_landing_who_get(client):
    response = client.get('/')
    assert response.status_code == 200  # page loads successfully

def test_landing_who_with_cookie(client):
    client.set_cookie('userdetails', 'I am a 23 year-old Asian woman with oily sensitive skin and light-medium complexion')
    response = client.get('/')
    assert response.status_code == 302  # redirect
    assert response.location == url_for('landing_what')