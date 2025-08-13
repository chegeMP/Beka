def test_home_page(client):
    """Test the home page returns 200 OK"""
    response = client.get('/')
    assert response.status_code == 200

def test_404_page(client):
    """Test 404 page handling"""
    response = client.get('/nonexistent')
    assert response.status_code == 404