from collections.abc import Callable
from bstream import BinaryStream


def read_dummy_optional(out: BinaryStream):
    dummy = out.read_byte()
    if dummy != 1:
        raise ValueError("Expected dummy byte to be 1")

def write_dummy_optional(out: BinaryStream):
    out.write_bool(True)


def read_optional[T](stream: BinaryStream, reader: Callable[[BinaryStream], T]) -> T | None:
    if stream.get_bool():
        return reader(stream)
    return None

def write_optional[T](out: BinaryStream, value: T|None, writer: Callable[BinaryStream, T]):
    if value is not None:
        out.write_bool(True)
        writer(out, value)
    else:
        out.write_bool(False)


def read_double_optional[T](stream: BinaryStream, reader: Callable[[BinaryStream], T]) -> T | None:
    read_dummy_optional(stream)
    return read_optional(stream, reader)

def write_double_optional[T](out: BinaryStream, value: T|None, writer: Callable[BinaryStream, T]):
    write_dummy_optional(out)
    write_optional(out, value, writer)


def read_list[T](stream: BinaryStream, reader: Callable[[BinaryStream], T]) -> list[T]:
    count = stream.get_unsigned_varint()
    result = []
    for _ in range(count):
        result.append(reader(stream))
    return result

def write_list[T](stream: BinaryStream, a_list: list[T], writer: Callable[[BinaryStream, T], None]) -> None:
    stream.write_unsigned_varint(len(a_list))
    for item in a_list:
        writer(stream, item)
