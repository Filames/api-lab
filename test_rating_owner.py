# The other user must not read the rating of the owner.
def test_other_cannot_read(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"
    res = api.get(path, headers=other_auth)
    assert 400 <= res.status_code <= 499

    # Owner can still read it
    res = api.get(path, headers=auth)
    assert res.status_code == 200
    assert res.json() == rating


# The other user must not change the rating of the owner.
def test_other_cannot_update(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": 1}, headers=other_auth)
    assert 400 <= res.status_code <= 499

    # Owner reads back and rating is unchanged
    res = api.get(path, headers=auth)
    assert res.status_code == 200
    assert res.json()["stars"] == rating["stars"]


# The other user must not delete the rating of the owner.
def test_other_cannot_delete(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"
    res = api.delete(path, headers=other_auth)
    assert 400 <= res.status_code <= 499

    # Owner reads back and rating still exists
    res = api.get(path, headers=auth)
    assert res.status_code == 200
    assert res.json() == rating
