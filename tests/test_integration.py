from app import app, db, Temperature


def test_homepage_with_database():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/")

        assert response.status_code == 200
        assert b"TempConverter" in response.data
        assert b"Algebra Bernays University" in response.data


def test_conversion_saved_to_database():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        response = client.post(
            "/",
            data={"celsius": "25"},
            headers={"User-Agent": "TempConverterIntegrationTest"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
            follow_redirects=True,
        )

        assert response.status_code == 200

    with app.app_context():
        temperature = (
            Temperature.query
            .order_by(Temperature.id.desc())
            .first()
        )

        assert temperature is not None
        assert temperature.celsius == 25
        assert temperature.fahrenheit == 77
