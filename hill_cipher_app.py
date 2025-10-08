import streamlit as st
import numpy as np

# ---------- Hill Cipher Functions ----------
def clean_text_letters_only(text):
    return ''.join(c.upper() if c.isalpha() else '_' for c in text)

def text_to_numbers(text):
    return [ord(c) - ord('A') for c in text if c != '_']

def numbers_to_text(numbers):
    text = ''.join(chr(int(n) + ord('A')) for n in numbers)
    return text

def mod_inv(a, m):
    for i in range(1, m):
        if (a * i) % m == 1:
            return i
    raise ValueError(f"No modular inverse for {a} under mod {m}")

def mod_matrix_inverse(matrix, modulus):
    det = int(round(np.linalg.det(matrix))) % modulus
    det_inv = mod_inv(det, modulus)
    adjugate = np.array([[matrix[1,1], -matrix[0,1]],
                         [-matrix[1,0], matrix[0,0]]])
    return (det_inv * adjugate) % modulus

def hill_encrypt(plaintext, matrix):
    plaintext = clean_text_letters_only(plaintext)
    letters_only = plaintext.replace('_','')
    if len(letters_only) % 2 != 0:
        letters_only += 'X'

    nums = text_to_numbers(letters_only)
    ciphertext_nums = []
    for i in range(0, len(nums), 2):
        pair = np.array(nums[i:i+2])
        enc = matrix.dot(pair) % 26
        ciphertext_nums.extend(enc)

    ciphertext = numbers_to_text(ciphertext_nums)
    encrypted_with_spaces = ''
    letter_idx = 0
    for c in plaintext:
        if c == '_':
            encrypted_with_spaces += '_'
        else:
            encrypted_with_spaces += ciphertext[letter_idx]
            letter_idx += 1
    return encrypted_with_spaces

def hill_decrypt(ciphertext, matrix_inv):
    space_positions = [i for i, c in enumerate(ciphertext) if c == '_']
    letters_only = ciphertext.replace('_','')

    nums = text_to_numbers(letters_only)
    plaintext_nums = []
    for i in range(0, len(nums), 2):
        pair = np.array(nums[i:i+2])
        dec = matrix_inv.dot(pair) % 26
        plaintext_nums.extend(dec)

    plaintext = numbers_to_text(plaintext_nums)
    plaintext_with_spaces = ''
    letter_idx = 0
    for i in range(len(ciphertext)):
        if i in space_positions:
            plaintext_with_spaces += ' '
        else:
            plaintext_with_spaces += plaintext[letter_idx]
            letter_idx += 1
    return plaintext_with_spaces.rstrip('X')

def keyword_to_matrix(keyword):
    keyword = clean_text_letters_only(keyword).replace('_','')
    if len(keyword) < 4:
        raise ValueError("Keyword must have at least 4 letters for 2x2 matrix")
    nums = [ord(c) - ord('A') for c in keyword[:4]]
    return np.array([[nums[0], nums[1]], [nums[2], nums[3]]])

# ---------- Streamlit App ----------
st.title("Hill Cipher Encryption/Decryption")

# Choose operation
operation = st.radio("Select Operation", ("Encrypt", "Decrypt"))

# Key type
key_type = st.radio("Key Type", ("Keyword", "Numeric 2x2 Matrix"))

# Key input
if key_type == "Keyword":
    keyword = st.text_input("Enter keyword (at least 4 letters)")
    if keyword:
        K = keyword_to_matrix(keyword)
        try:
            K_inv = mod_matrix_inverse(K, 26)
        except:
            st.error("Keyword matrix is not invertible!")
else:
    a = st.number_input("Enter a11 (0-25)", 0, 25, 7)
    b = st.number_input("Enter a12 (0-25)", 0, 25, 8)
    c = st.number_input("Enter a21 (0-25)", 0, 25, 11)
    d = st.number_input("Enter a22 (0-25)", 0, 25, 11)
    K = np.array([[a, b], [c, d]])
    try:
        K_inv = mod_matrix_inverse(K, 26)
    except:
        st.error("Matrix is not invertible!")

# Text input
text_input = st.text_area("Enter text here")

# Execute encryption/decryption
if st.button("Run"):
    if not text_input:
        st.warning("Please enter text to proceed.")
    else:
        if operation == "Encrypt":
            result = hill_encrypt(text_input, K)
        else:
            result = hill_decrypt(text_input, K_inv)
        st.success(f"Result:\n{result.replace('_',' ')}")
