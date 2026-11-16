from queue import Empty, Queue
from threading import Thread

from cryptography.cobblestone import (
    Cobblestone128Decryptor,
    Cobblestone128Encryptor,
)

key = Cobblestone128Encryptor.generate_key()
context = b"cryptography-test"

def encrypt(read_queue: Queue, transmit_queue_a: Queue, transmit_queue_b: Queue):
    encryptor = Cobblestone128Encryptor(key, context)
    while True:
        line = read_queue.get()
        try:
            packet = encryptor.update(line.encode())
        except AttributeError:
            break
        if packet != b"":
            transmit_queue_a.put(packet)
            transmit_queue_b.put(packet)
    finalize = encryptor.finalize()
    transmit_queue_a.put(finalize)
    transmit_queue_b.put(finalize)
    transmit_queue_a.put(b"") # empty byte to indicate end of transmission
    transmit_queue_b.put(b"")

def decrypt(read_queue: Queue, output_queue: Queue):
    decryptor = Cobblestone128Decryptor(key, context)
    while True:
        packet = read_queue.get()
        if packet == b"":
            break
        else:
            decrypted = decryptor.update(packet)
            if decrypted != b"":
                output_queue.put(decrypted)
    finalize = decryptor.finalize()
    output_queue.put(finalize)
    output_queue.put(b"")

def encode(file_lines: list[str], transmit_queue: Queue):
    for line in file_lines:
        transmit_queue.put(line)
    transmit_queue.put(b"")

def ensure_encrypted(file_contents: str, read_queue: Queue, expected_chunks: list[int]):
    total = b""
    i = 0
    while True:
        packet = read_queue.get()
        if packet == b"":
            break
        assert len(packet) == expected_chunks[i]
        total += packet
        try:
            cut_file = file_contents.replace(packet.decode(), "")
            assert(len(cut_file) == len(file_contents))
            # essentially, assert that we cannot find the decoded packet
        except UnicodeDecodeError:
            pass
    try:
        cut_file = file_contents.replace(total.decode(), "")
        assert(len(cut_file) == len(file_contents))
        # essentially, assert that we cannot find the decoded packet
    except UnicodeDecodeError:
        pass

def decode_eval(file_contents: str, read_queue: Queue, output_queue: Queue | None = None):
    src_string = file_contents
    string = ""
    while True:
        packet = read_queue.get()
        if packet == b"":
            break
        old_len = len(src_string)
        src_string = src_string.replace(packet.decode(), "")
        assert(len(src_string) < old_len)
        string += packet.decode()

    if output_queue is not None:
        output_queue.put(string)
    assert(string == file_contents)

def eval_cobblestone_on_stream(data: str, expected_chunks: list[int]):
    """
    Sets up a pipeline composed of several threads to test the Cobblestone
    streaming encryption recipe. The steps include:

    1. Encoding a long text stream into short queued segments (by line)
    2. Encrypting the plaintext segments using Cobblestone
    3. Ensuring that the encrypted segments match spec and do not contain useful plaintext
    4. Decrypting the Cobblestone packets
    5. Decoding the decrypted packets and comparing them against the source data
    """

    encoded = Queue()
    mock_socket_a = Queue() # gets decrypted
    mock_socket_b = Queue() # gets checked for spec/useful data
    decrypted = Queue()

    threads: list[Thread] = []

    lines: list[str]
    with open(data) as example_data:
        lines = example_data.readlines()

    threads.append(Thread(target=encode, args=[lines, encoded]))
    threads.append(Thread(target=encrypt, args=[encoded, mock_socket_a, mock_socket_b]))
    threads.append(Thread(target=ensure_encrypted, args=["".join(lines), mock_socket_b, expected_chunks]))
    threads.append(Thread(target=decrypt, args=[mock_socket_a, decrypted]))
    threads.append(Thread(target=decode_eval, args=["".join(lines), decrypted]))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

def test_short_stream():
    """ensures correct behavior for a short (few hundred byte) example"""
    eval_cobblestone_on_stream("integration_testing/example_short.txt", [56, 237])

def test_long_stream():
    """ensures correct behavior for a longer (~98kb) example"""
    chunk_lengths = [56, 16400, 16400, 16400, 16400, 16400, 9442]
    eval_cobblestone_on_stream("integration_testing/example_short.txt", chunk_lengths)
