from config import hashing


def hash_prep(val_a, val_b):
    val_a_hash = hashing.hash_value(val_a)
    val_b_hash = hashing.hash_value(val_b)
    return hashing.hash_value(val_a_hash, val_b_hash)
