import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_app_creation():
    """Test that the app can be created"""
    app = create_app()
    assert app is not None
    assert app.config['TESTING'] == False

def test_database_connection(app):
    """Test database connection"""
    with app.app_context():
        # Test that we can query the database
        result = db.engine.execute('SELECT 1').fetchone()
        assert result[0] == 1
