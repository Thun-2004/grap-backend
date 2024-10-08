from fastapi.testclient import TestClient

from api import app
from api.configuration import Configuration
from api.dependencies.configuration import get_configuration
from api.models.customer import Customer

import jwt


def test_customer(configuration_fixture: Configuration):
    app.dependency_overrides[get_configuration] = lambda: configuration_fixture
    test_client = TestClient(app)
    register_response = test_client.post(
        "/customers/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "test@gmail.com",
            "password": "password",
        },
    )

    assert register_response.status_code == 200
    decoded_id = jwt.decode(  # type:ignore
        register_response.json()["jwt_token"],
        configuration_fixture.jwt_secret,
        algorithms=["HS256"],
    )["customer_id"]
    assert decoded_id == register_response.json()["id"]

    with configuration_fixture.create_session() as session:
        result = (
            session.query(Customer).filter_by(id=decoded_id).first()
        )


    assert result is not None

    assert result.first_name == "John"  # type:ignore
    assert result.last_name == "Doe"  # type:ignore
    assert result.username == "johndoe"  # type:ignore
    assert result.email == "test@gmail.com"  # type:ignore
    assert result.id == decoded_id  # type:ignore

    failed_get_response = test_client.post(
        "/customers/register",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "test@gmail.com",
            "password": "password",
        },
    )

    assert failed_get_response.status_code == 409

    login_response = test_client.post(
        "/customers/login",
        json={"username": "johndoe", "password": "password"},
    )

    assert login_response.status_code == 200

    logged_in_id = jwt.decode(  # type:ignore
        login_response.json()["jwt_token"],
        configuration_fixture.jwt_secret,
        algorithms=["HS256"],
    )["customer_id"]

    assert result.id == logged_in_id

    failed_login_response = test_client.post(
        "/customers/login",
        json={"username": "johndoe", "password": "wrongpassword"},
    )

    assert failed_login_response.status_code == 401

    failed_login_response = test_client.post(
        "/customers/login",
        json={"username": "wrongusername", "password": "password"},
    )

    assert failed_login_response.status_code == 401

    get_response =  test_client.get("/customers/me", headers={
        "Authorization": f"Bearer {register_response.json()["jwt_token"]}"
    })

    assert get_response.status_code == 200
    assert result.id == get_response.json()["id"]

    failed_get_response = test_client.get("/customers/me", headers={
        "Authorization": "Bearer Invalid"
    })

    assert failed_get_response.status_code == 401
