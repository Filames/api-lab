import pytest


# The pizza never needs a tool that the customer excluded.
@pytest.mark.parametrize("excluded", [
    ["Knife"],
    ["Scissors"],
    [],
    ["Knife", "Scissors"],
])
def test_excluded_tool_is_not_used(api, auth, excluded):
    body = {"excludedTools": excluded}
    res = api.post("/api/pizza", json=body, headers=auth)
    assert res.status_code == 200
    assert res.json()["pizza"]["tool"] not in excluded


# Defect 1: Excluding all three tools returns 500 instead of 400.
@pytest.mark.xfail(
    reason="Defect 1: excluding all three tools returns 500 with empty body instead of 400 with error message",
    strict=True,
)
def test_exclude_all_tools_gives_error(api, auth):
    body = {"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}
    res = api.post("/api/pizza", json=body, headers=auth)
    assert res.status_code == 400
    assert "error" in res.json()
