import pytest
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    """Setup test client for Flask app"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_data():
    """Mock structure representing data.json"""
    return {
        "children": [
            {"id": 1, "name": "Test Child 1", "balance": 100.0, "is_active": True, "history": []},
            {"id": 2, "name": "Test Child 2", "balance": 50.0, "is_active": False, "history": []}
        ]
    }

@patch('app.is_authenticated', return_value=True)
@patch('app.save_data')
@patch('app.get_data')
def test_deposit_increases_balance(mock_get_data, mock_save_data, mock_auth, client, mock_data):
    # Arrange
    # Set up mocked data so get_data() returns our test structure
    mock_get_data.return_value = mock_data
    
    # Act
    # Perform POST request, simulating a 20.0 deposit to the account of child with ID 1
    response = client.post('/api/transaction', json={
        "child_id": 1,
        "amount": 20.0,
        "description": "Allowance"
    })
    
    # Assert
    # Check if request was successful (status 200 OK)
    assert response.status_code == 200
    assert response.json["success"] is True
    
    # Verify that save_data was called with correct data
    assert mock_save_data.called
    saved_data = mock_save_data.call_args[0][0]
    
    # Check if balance increased from 100.0 to 120.0
    assert saved_data["children"][0]["balance"] == 120.0
    
    # Check if transaction was saved in history
    assert len(saved_data["children"][0]["history"]) == 1
    assert saved_data["children"][0]["history"][0]["amount"] == 20.0

@patch('app.is_authenticated', return_value=True)
@patch('app.save_data')
@patch('app.get_data')
def test_expense_decreases_balance(mock_get_data, mock_save_data, mock_auth, client, mock_data):
    # Arrange
    # Set up initial balance of 100.0
    mock_get_data.return_value = mock_data
    
    # Act
    # Send expense request (-15.0)
    response = client.post('/api/transaction', json={
        "child_id": 1,
        "amount": -15.0,
        "description": "Toy"
    })
    
    # Assert
    # Ensure operation succeeded and balance dropped to 85.0
    assert response.status_code == 200
    saved_data = mock_save_data.call_args[0][0]
    assert saved_data["children"][0]["balance"] == 85.0

@patch('app.is_authenticated', return_value=True)
@patch('app.save_data')
@patch('app.get_data')
def test_deposit_zero_amount(mock_get_data, mock_save_data, mock_auth, client, mock_data):
    # Arrange
    # Prepare data with balance of 100.0
    mock_get_data.return_value = mock_data
    
    # Act
    # Send amount 0.0 (edge case)
    response = client.post('/api/transaction', json={
        "child_id": 1,
        "amount": 0.0,
        "description": "Nothing"
    })
    
    # Assert
    # Even for 0.0 value, the operation should pass, but the balance must not change
    assert response.status_code == 200
    saved_data = mock_save_data.call_args[0][0]
    assert saved_data["children"][0]["balance"] == 100.0

@patch('app.is_authenticated', return_value=True)
@patch('app.save_data')
@patch('app.get_data')
def test_transaction_invalid_amount_format(mock_get_data, mock_save_data, mock_auth, client, mock_data):
    # Arrange
    # Account state unchanged
    mock_get_data.return_value = mock_data
    
    # Act
    # Provide non-numeric string as amount
    response = client.post('/api/transaction', json={
        "child_id": 1,
        "amount": "not-a-number",
        "description": "Error test"
    })
    
    # Assert
    # Expect status 400 (Bad Request) and no data saving
    assert response.status_code == 400
    assert "Invalid amount" in response.json["error"]
    mock_save_data.assert_not_called()

@patch('app.is_authenticated', return_value=True)
@patch('app.save_data')
@patch('app.get_data')
def test_transaction_missing_parameters(mock_get_data, mock_save_data, mock_auth, client, mock_data):
    # Arrange
    mock_get_data.return_value = mock_data
    
    # Act
    # Missing amount parameter
    response = client.post('/api/transaction', json={
        "child_id": 1,
        "description": "Missing amount"
    })
    
    # Assert
    # We should receive status 400 with appropriate error message
    assert response.status_code == 400
    assert "Missing parameters" in response.json["error"]
    mock_save_data.assert_not_called()

@patch('app.is_authenticated', return_value=True)
@patch('app.save_data')
@patch('app.get_data')
def test_transaction_nonexistent_child(mock_get_data, mock_save_data, mock_auth, client, mock_data):
    # Arrange
    mock_get_data.return_value = mock_data
    
    # Act
    # Transaction for a child whose ID does not exist in mock_data (e.g., 99)
    response = client.post('/api/transaction', json={
        "child_id": 99,
        "amount": 10.0,
        "description": "Ghost child"
    })
    
    # Assert
    # Error 404 (Not Found) and no call to save to json
    assert response.status_code == 404
    assert "Child not found" in response.json["error"]
    mock_save_data.assert_not_called()

