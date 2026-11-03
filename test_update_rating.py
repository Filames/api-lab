import pytest


# Boundary values: update stars to 0, 1, 5, 6 and check results.
# Stars 1 and 5 are saved (200), stars 0 and 6 are refused (400).
@pytest.mark.parametrize("stars,expected_status", [
    (0, 400),
    (1, 200),
    (5, 200),
    (6, 400),
])
def test_update_stars_boundary(api, auth, rating, stars, expected_status):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": stars}, headers=auth)
    assert res.status_code == expected_status

    # Read the rating back and check stars
    res = api.get(path, headers=auth)
    assert res.status_code == 200
    if expected_status == 200:
        assert res.json()["stars"] == stars
    else:
        # A refused update must leave the rating unchanged
        assert res.json()["stars"] == rating["stars"]
