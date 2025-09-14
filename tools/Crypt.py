from cryptography.fernet import Fernet
import bcrypt

# Tạo khóa mã hóa và băm mật khẩu
def create_password_hash(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Mã hóa và giải mã IP với Fernet
def encrypt_ip(ip_address: str, key: bytes) -> str:
    fernet = Fernet(key)
    encrypted_ip = fernet.encrypt(ip_address.encode()).decode()
    return encrypted_ip

def decrypt_ip(encrypted_ip: str, key: bytes) -> str:
    fernet = Fernet(key)
    decrypted_ip = fernet.decrypt(encrypted_ip.encode()).decode()
    return decrypted_ip

def decrypt_ip1(encrypted_ip: str, key: str) -> str:
    # Nếu key là chuỗi dạng "b'...'" thì cần xử lý:
    if key.startswith("b'") and key.endswith("'"):
        key = key[2:-1]  # Cắt b'...'
    fernet = Fernet(key.encode())  # Mã hóa lại thành bytes
    decrypted_ip = fernet.decrypt(encrypted_ip.encode()).decode()
    return decrypted_ip
# Mã hóa mật khẩu bằng bcrypt
password = "123"
hashed_password = create_password_hash(password)
print(f"Đã băm mật khẩu: {hashed_password}")

#giải mã mật khẩu
def check_password(hashed_password: bytes, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


# Mã hóa địa chỉ IP với Fernet
key = Fernet.generate_key()  # Tạo khóa Fernet (sử dụng một lần duy nhất và lưu lại)
ip_address = "192.168.100.14"
encrypted_ip = encrypt_ip(ip_address, key)
print(f"Đã mã hóa IP: {encrypted_ip}")
print(f"Khóa mã hóa: {key}")
#in class của khóa mã hóa
# print(f"Class của khóa mã hóa: {type(key)}")
# encrypt_ip1 = "gAAAAABoBdUtSABFhAX2_CaVhOX_iL-w6vRwyPNc-fwPBTvcj31eZIPm9tX-snybyIRRytDq_8jveJ6qGWw8R5InaSBUofpnyQ=="
# key1 = "b'Kpv2xwHOOjRRRDp8OsNCjRWKGLKcaYDGeZSxEXMYN5w='"
# # Giải mã IP
# decrypted_ip = decrypt_ip1(encrypt_ip1, key1)
# print(f"Giải mã IP: {decrypted_ip}")
