"""Utility script to seed the MongoDB database with initial activities."""
from db import seed_if_empty

if __name__ == "__main__":
    seed_if_empty()
    print("Seed complete")
