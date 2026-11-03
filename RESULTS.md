# API lab results

## Part 0
- Step 0.1, the number of pizza names: 18
- Step 0.3, status code of the request without a token: 401
- Step 0.4, the name of your pizza: The Dead Hawaii
- Step 0.12, results of the three runs without a session (optional): Run 1: FAILED (assert 401 == 200), Run 2: PASSED (status code 200), Run 3: FAILED (assert 401 == 200)
- Step 0.16, blocks of "how many of the three tools are excluded":
  - 0 tools excluded: `[]`
  - 1 tool excluded: `["Knife"]` or `["Scissors"]`
  - 2 tools excluded: `["Knife", "Scissors"]`
  - 3 tools excluded: `["Knife", "Pizza cutter", "Scissors"]`

## Defect report
- Title: Server returns 500 Internal Server Error when all three tools are excluded
- Request: `POST https://quickpizza.grafana.com/api/pizza` with header `Authorization: token <valid-token>` and body `{"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}`
- Expected result: Status code 400 Bad Request with a descriptive JSON error message explaining that no pizza can satisfy the request (e.g. `{"error": "no pizza can satisfy the request"}`).
- Actual result: Status code 500 Internal Server Error with an empty body (`Content-Length: 0`).
- Severity: Medium (Causes unhandled server-side failure instead of proper input validation and error feedback when an impossible combination of constraints is provided).

## Part A
- Step A4, status codes when the other user reads, changes and deletes:
  - Read: 404 Not Found (response: `{"error":"not found"}`)
  - Change: 400 Bad Request (response: `{"error":"rating ID <id> not found"}`)
  - Delete: 400 Bad Request (response: `{"error":"rating ID <id> not found"}`)

## Part B
1. **Two kinds of failure an API test can find that a unit test with stubs cannot:**
   - Real network, environment, and protocol integration issues: Examples include HTTP status code discrepancies, payload serialization/deserialization mismatches, and load balancer cookie/session handling (such as `AWSALB`).
   - Server-side runtime errors and unhandled exceptions: For example, an unhandled exception resulting in HTTP 500 Internal Server Error on the live backend when specific constraint combinations (such as excluding all cutting tools) are passed.
   
   **One reason to write unit tests with stubs as well:**
   - Unit tests execute orders of magnitude faster (in milliseconds without network latency), are fully deterministic and isolated from external dependencies (avoiding network flakiness, rate limiting, and server downtime), and can easily simulate hard-to-reach edge cases (such as connection timeouts or unexpected server crashes).

2. **Why every test creates its own user with a new name rather than using the public token:**
   - QuickPizza is a shared environment accessed concurrently by multiple users and automated test runs. If tests share the same user account or public token, concurrent tests will read, modify, or delete each other's data (test pollution and race conditions). Creating a fresh, uniquely named user per test ensures test isolation and reproducibility.
   
   **Applying this to Project 2:**
   - In Project 2 (testing the shared shop or hotel API), each test or test run should create its own uniquely partitioned resources (e.g., using random UUIDs or distinct group prefixes for customer names, cart sessions, or room bookings) and clean them up after execution so tests never interfere with other groups' data.

3. **Why tests send every request through one session:**
   - QuickPizza operates on multiple backend servers behind a load balancer. When a user is created on one server instance, that user only exists on that specific instance. The load balancer issues sticky session cookies (`AWSALB` and `AWSALBCORS`). By using a single `requests.Session` across requests, the client automatically stores and resends these cookies with every call, ensuring that all related requests route to the identical backend server.
   
   **Step 0.12 observations:**
   - Without a session, each request is sent standalone without cookies. In our 3 runs:
     - Run 1 failed with 401 Unauthorized during login (`assert 401 == 200`) because the login request hit a different server that did not know the user.
     - Run 2 passed (200 OK) because the load balancer randomly hit the same server instance.
     - Run 3 failed with 401 Unauthorized (`assert 401 == 200`) because it again reached a different server instance. This demonstrated that tests without session affinity are flaky.

4. **Excluded tools block that revealed the defect in Step 0.16:**
   - The block with 3 tools excluded: `["Knife", "Pizza cutter", "Scissors"]`.
   
   **Why 500 with empty body is worse than 400 with a message:**
   - A 500 Internal Server Error indicates an unexpected, unhandled crash on the server. The empty body provides no explanation to client applications, leaving them unable to determine whether the server is completely down or if the request was simply unsatisfied. In contrast, a 400 Bad Request with a clear JSON error message informs the client that the request broke domain rules, allowing the client application to display a helpful message to the user.
   
   **Why the test stays as `xfail` instead of being deleted:**
   - Keeping the test as `@pytest.mark.xfail(strict=True)` documents the known defect and keeps it tracked without breaking continuous integration runs. If deleted, regression tracking is lost. With `strict=True`, pytest will immediately fail the suite when QuickPizza fixes the defect (reporting an unexpected pass, `XPASS`), prompting developers to update the test expectation and remove the `xfail` marker.

5. **Test counts for Base Choice Coverage (BCC) vs. All Combinations (AC) for Step A1:**
   - Characteristics and blocks:
     - C1 (Value of stars): 3 blocks (`below 1`, `1 to 5` [base], `above 5`)
     - C2 (Type of stars): 4 blocks (`whole number` [base], `decimal`, `text`, `missing`)
     - C3 (Pizza): 2 blocks (`exists` [base], `does not exist`)
     - C4 (Token): 3 blocks (`user's own` [base], `none`, `wrong length`)
   
   - **Base Choice Coverage:**
     - 1 base test (all characteristics at base block)
     - C1 non-base: 3 - 1 = 2 tests
     - C2 non-base: 4 - 1 = 3 tests
     - C3 non-base: 2 - 1 = 1 test
     - C4 non-base: 3 - 1 = 2 tests
     - Total = 1 + 2 + 3 + 1 + 2 = **9 tests**.
   
   - **All Combinations Coverage:**
     - Total = 3 × 4 × 2 × 3 = **72 tests**.

6. **Status codes from Step A4 and defect analysis:**
   - Actual status codes obtained:
     - Read: `404 Not Found`
     - Change (PUT): `400 Bad Request`
     - Delete (DELETE): `400 Bad Request`
   - Expected status codes:
     - Standard RESTful authorization expects `403 Forbidden` when an authenticated user attempts to access or modify a resource owned by another user.
     - Alternatively, if the API chooses to hide resource existence to avoid enumeration attacks, it should consistently return `404 Not Found` across all three operations (GET, PUT, DELETE).
   - Is it a defect?
     - Yes. Returning `400 Bad Request` for PUT and DELETE is incorrect HTTP semantics because the request syntax and body format are valid. Furthermore, the response bodies explicitly claim `"rating ID <id> not found"`, directly contradicting the `400 Bad Request` status code by describing a missing resource condition (`404`) under a syntax error code (`400`).

7. **Made-up token test results and implications:**
   - What comes back: The API returns `200 OK` with a JSON list containing public ratings: `{"ratings":[{"id":1,"stars":5,"pizza_id":1}, ...]}`.
   - Is this a defect: Yes, this is an authentication defect (Broken Authentication / Improper Token Validation).
   - Potential impact: The API fails to validate whether the token belongs to an active, valid registered session, accepting any arbitrary 16-character string. On a real system, an attacker could forge tokens to bypass authentication, harvest user ratings, or access endpoints without ever registering or authenticating.

8. **API test vs. Web page test comparison:**
   - **Better checked by an API test:** Accurate HTTP response codes, headers (content types, caching headers, session cookies), exact JSON payload types, boundary value validation directly against backend logic, and fast regression test execution.
   - **Only checkable by a web page test:** User interface visual presentation, CSS layouts across responsive breakpoints, client-side rendering behaviors, accessibility, animation smoothness, and end-user visual feedback.
