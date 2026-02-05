from auth import hash_password, verify_password

fake_user = {
    "username": "carlos",
    "hashed_password": hash_password("password123")
}

def authenticate_user(username: str, password: str):
    if username != fake_user["username"]:
        return None
    if not verify_password(password, fake_user["hashed_password"]):
        return None
    return {"username": username}
