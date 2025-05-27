#one-time usage

from cryptography.fernet import Fernet
import os

def generate_and_save_key(env_path=".env"):
    key = Fernet.generate_key().decode()

    # Cek apakah file .env sudah ada
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(f"FERNET_KEY={key}\n")
        print(f".env created with FERNET_KEY: {key}")
    else:
        # Jika .env sudah ada, cek apakah sudah ada FERNET_KEY
        with open(env_path, "r") as f:
            lines = f.readlines()

        found = any("FERNET_KEY=" in line for line in lines)

        if found:
            print("FERNET_KEY already exists in .env, not overwriting.")
        else:
            with open(env_path, "a") as f:
                f.write(f"FERNET_KEY={key}\n")
            print(f"FERNET_KEY added to existing .env: {key}")

if __name__ == "__main__":
    generate_and_save_key()
