from itkit.create_users import make_username, make_password, process_users


def test_username_is_initial_plus_surname():
    assert make_username("Tom", "Baker", set()) == "tbaker"


def test_duplicate_usernames_get_a_number():
    assert make_username("Tara", "Baker", {"tbaker"}) == "tbaker2"


def test_password_meets_complexity():
    pw = make_password()
    assert len(pw) == 12 and any(c.isdigit() for c in pw) and any(c.isupper() for c in pw)


def test_invalid_rows_are_reported_not_crashed():
    rows = [
        {"first_name": "Lee", "last_name": "Chen", "department": "Sales", "email": "bad@email"},
        {"first_name": "", "last_name": "Okafor", "department": "IT", "email": "j@example.com"},
        {"first_name": "Amira", "last_name": "Khan", "department": "Finance", "email": "a@example.com"},
    ]
    accounts, errors = process_users(rows)
    assert len(accounts) == 1 and len(errors) == 2
