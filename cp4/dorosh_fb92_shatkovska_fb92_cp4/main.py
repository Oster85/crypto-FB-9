# # This is the 4th lab on Cryptology yet in progress by Dorosh and Shatkovska FB-92
import random

rand = random.SystemRandom()
import math


# from lab3
def gcd(a, b):
    p = [0, 1]
    gcd_val = b
    a, b = max(a, b), min(a, b)
    while b != 0:
        q = a // b
        gcd_val = b
        a, b = b, a % b
        p.append(p[-1] * (-q) + p[-2])
    return gcd_val, p[-2]  # returns gdc and a^-1


def decompose(p):
    # decomposes p to s and d values in p-1 = d* 2^s
    d = p - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    return s, d


# http://rosettacode.org/wiki/Miller%E2%80%93Rabin_primality_test#Python
# Miller-Rabin primality test
def miller_rabin(p, k):
    # part 0
    s, d = decompose(p)
    counter = 0
    while counter < k:
        # part 1
        x = rand.randint(1, p)
        if gcd(x, p)[0] > 1:
            return False
        elif gcd(x, p)[0] == 1:
            # part 2
            if abs(pow(x, d, p)) == 1:
                continue
            else:
                xr = pow(x, 2 * d, p)  # if r == 1
                for r in range(2, s - 1):
                    xr = pow(xr, d * (2 ** r), p)
                    if xr == -1:
                        continue
                    elif xr == -1:
                        return False
        counter += 1
    return True


# print(miller_rabin(97, 10))             # prime
# print(miller_rabin(21881, 10))          # prime


def generate_prime(bits):
    while True:
        a = (rand.randrange(1 << bits - 1, 1 << bits) << 1) + 1  # making sure its odd
        if miller_rabin(a, 20):
            return a


# print(generate_prime(256))


def generate_pq_pair(bits):
    pair0 = (generate_prime(bits), generate_prime(bits))
    return pair0

    # while True:
    #     pair1 = (generate_prime(bits), generate_prime(bits))
    #     if pair0[0]*pair0[1] <= pair1[0]*pair1[1]:
    #         return pair0, pair1


print(generate_pq_pair(256))


def generate_e(phin):
    while True:
        e = rand.randrange(2, phin)
        if gcd(e, phin) == 1:
            return e


def decode(message):
    message = int(message.encode('utf-8').hex(), 16)
    return message


def encode(message):
    message = bytes.fromhex(hex(message)).decode('utf-8')
    return message


class User:
    def __init__(self):
        self.p = 0
        self.q = 0
        self.n = 0
        self.e = 0
        self.d = 0
        self.other_e = 0
        self.other_n = 0

    def generate_keys(self):
        bits = 256
        self.p, self.q = generate_pq_pair(bits)
        self.n = self.p * self.q
        phin = (self.p - 1) * (self.q - 1)
        self.e = generate_e(phin)
        self.d = gcd(self.e, phin)[1]
        return self.n, self.e

    # !!!may be combined with generate_keys() later
    def generate_correct_keys(self):  # for user A to choose correct keys (other.n <= n)
        while self.other_n > self.generate_keys()[0]:
            continue

    def encrypt(self, message):  # message needs to be decoded from utf-8
        encrypted = pow(message, self.other_e, self.other_n)
        return encrypted

    def decrypt(self, message):
        decrypted = pow(message, self.d, self.n)
        return decrypted  # message needs to be encoded as utf-8

    def sign(self, message):
        signed = pow(message, self.d, self.n)
        signed_encrypted = self.encrypt(signed)
        return signed_encrypted

    def verify(self, signed, decrypted_message):
        return self.encrypt(signed) == decrypted_message

    def send_keys(self):
        return self.e, self.n

    def receive_keys(self, other_e, other_n):
        self.other_e = other_e
        self.other_n = other_n

    def send_message(self, text):
        message = decode(text)
        encrypted = self.encrypt(message)
        signed = self.sign(message)
        encrypted_signed = self.encrypt(signed)

        return encrypted, encrypted_signed

    def receive_message(self, encrypted, encrypted_signed):
        decrypted_message = self.decrypt(encrypted)
        signed = self.decrypt(encrypted_signed)

        if self.verify(signed, decrypted_message):
            return encode(decrypted_message)
        else:
            return -1


# full process of A sending a message to B
# B creates its keys and shares open keys (eb, nb) with A
B = User()
B.generate_keys()

# A receives keys
A = User()
A.receive_keys(B.send_keys())

# A creates its keys (nb < na) and shares its keys (ea, na) with B
# B receives A's keys and message
A.generate_correct_keys()
B.receive_keys(A.send_keys())

# A sends signed message and encrypted message to B
# B receives A's message, decrypts signed message and encrypted message and verifies signed message
M = "Hi there!"
received = B.receive_message(A.send_message(M))
print(received)