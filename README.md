# API Testing with pytest and requests (`api-lab`)

This repository contains automated API tests for the QuickPizza API (`https://quickpizza.grafana.com`) using Python, `pytest`, and `requests`.

---

## 1. Setup and Installation

### Prerequisites
- Python 3.10 or newer (tested with Python 3.13)
- `pip`
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd api-lab
   ```

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Running the Tests

To run the entire test suite:
```bash
pytest -v
```

To run the test suite and generate a self-contained HTML report:
```bash
pytest -v --html=report.html --self-contained-html
```

To run a single test file or specific test:
```bash
pytest -v test_ratings.py
pytest -v test_ratings.py::test_delete_rating
```

---

## 3. Input Domain Model for Creating Ratings (Step A1 & A2)

Operation under test: `POST /api/ratings`

| Characteristic | Blocks | Values in the tests | Test covering the block |
| :--- | :--- | :--- | :--- |
| **C1: Value of `stars`** | below 1 | `0` | `test_stars_out_of_range[0]` |
| | 1 to 5 (base) | `3` | `test_base_choice_is_saved` |
| | above 5 | `6` | `test_stars_out_of_range[6]` |
| **C2: Type of `stars`** | whole number (base) | `3` | `test_base_choice_is_saved` |
| | decimal | `3.5` | `test_stars_decimal` |
| | text | `"3"` | `test_stars_text` |
| | missing | no field | `test_stars_missing` |
| **C3: Pizza** | exists (base) | a new pizza | `test_base_choice_is_saved` |
| | does not exist | `999999999` | `test_pizza_does_not_exist` |
| **C4: Token** | the user's own (base) | from `auth` | `test_base_choice_is_saved` |
| | none | no header | `test_no_token` |
| | wrong length | `token short` | `test_wrong_token_length` |

*Note: Base Choice Coverage requires 1 base test + (3-1) + (4-1) + (2-1) + (3-1) = 9 tests, all implemented in `test_create_rating.py`.*

---

## 4. Test Suite Structure

- `conftest.py`: Defines shared fixtures including `api` (session with sticky cookie persistence and base URL routing), `auth` (registers and logs in a unique user), `pizza_id` (fetches a new pizza), `rating` (creates a test rating and cleans it up after test execution), and `other_auth` (registers a second user).
- `test_names.py`: Tests GET `/api/names` to verify the list of pizza names.
- `test_tools.py`: Tests GET `/api/tools` with authorization header to verify available pizza-cutting tools.
- `test_pizza.py`: Tests POST `/api/pizza` with dietary restrictions (vegetarian) and verifies refusal without auth token.
- `test_users.py`: Tests user registration and verifies an initial empty rating history for new accounts.
- `test_ratings.py`: Tests full CRUD lifecycle of pizza ratings (Create, Read, Update, Delete) using isolated fixtures.
- `test_refused.py`: Tests negative validation scenarios on `/api/users` (duplicate username, wrong password, empty username).
- `test_excluded_tools.py`: Tests input partitioning for excluded tools and tracks Defect 1 (`xfail`).
- `test_create_rating.py`: Implements Base Choice Coverage for `POST /api/ratings` based on the Input Domain Model.
- `test_update_rating.py`: Implements boundary value analysis for updating ratings (`PUT /api/ratings/{id}`) with stars 0, 1, 5, and 6.
- `test_rating_owner.py`: Verifies authorization and access control ensuring a user cannot read, update, or delete another user's rating.
