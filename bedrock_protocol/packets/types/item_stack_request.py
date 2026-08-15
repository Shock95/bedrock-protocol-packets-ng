# Copyright © 2025 GlacieTeam. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# SPDX-License-Identifier: MPL-2.0

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from typing import List, Optional
from bstream import BinaryStream, ReadOnlyBinaryStream
from bedrock_protocol.packets.types.full_container_name import FullContainerName
from bedrock_protocol.packets.enums.item_stack_request_action_type import (
    ItemStackRequestActionType,
)


class ItemStackRequestSlotInfo:
    container: FullContainerName
    slot: int
    net_id: int

    def __init__(
        self,
        container: Optional[FullContainerName] = None,
        slot: int = 0,
        net_id: int = 0,
    ):
        self.container = container or FullContainerName()
        self.slot = slot
        self.net_id = net_id

    def write(self, stream: BinaryStream) -> None:
        self.container.write(stream)
        stream.write_byte(self.slot)
        stream.write_signed_int(self.net_id)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        self.container.read(stream)
        self.slot = stream.get_byte()
        self.net_id = stream.get_signed_int()

class ItemStackRequestAction:
    type: ItemStackRequestActionType

    def __init__(self, type: ItemStackRequestActionType = ItemStackRequestActionType.Invalid):
        self.type = type

    def write(self, stream: BinaryStream) -> None:
        pass

    @classmethod
    def read(cls, stream: ReadOnlyBinaryStream) -> Self:
        return cls()


class TransferBase(ItemStackRequestAction):
    amount: int
    source: ItemStackRequestSlotInfo
    destination: ItemStackRequestSlotInfo

    def __init__(
        self,
        type: ItemStackRequestActionType = ItemStackRequestActionType.Invalid,
        amount: int = 0,
        source: Optional[ItemStackRequestSlotInfo] = None,
        destination: Optional[ItemStackRequestSlotInfo] = None,
    ):
        super().__init__(type)
        self.amount = amount
        self.source = source or ItemStackRequestSlotInfo()
        self.destination = destination or ItemStackRequestSlotInfo()

    def write(self, stream: BinaryStream) -> None:
        stream.write_byte(self.amount)
        self.source.write(stream)
        self.destination.write(stream)

    @classmethod
    def read(cls, stream: ReadOnlyBinaryStream) -> Self:
        action = cls()
        action.amount = stream.get_byte()
        action.source.read(stream)
        action.destination.read(stream)
        return action


class TakeAction(TransferBase):
    def __init__(
        self,
        amount: int = 0,
        source: Optional[ItemStackRequestSlotInfo] = None,
        destination: Optional[ItemStackRequestSlotInfo] = None,
    ):
        super().__init__(ItemStackRequestActionType.Take, amount, source, destination)


class PlaceAction(TransferBase):
    def __init__(
        self,
        amount: int = 0,
        source: Optional[ItemStackRequestSlotInfo] = None,
        destination: Optional[ItemStackRequestSlotInfo] = None,
    ):
        super().__init__(ItemStackRequestActionType.Place, amount, source, destination)


class SwapAction(ItemStackRequestAction):
    source: ItemStackRequestSlotInfo
    destination: ItemStackRequestSlotInfo

    def __init__(
        self,
        source: Optional[ItemStackRequestSlotInfo] = None,
        destination: Optional[ItemStackRequestSlotInfo] = None,
    ):
        super().__init__(ItemStackRequestActionType.Swap)
        self.source = source or ItemStackRequestSlotInfo()
        self.destination = destination or ItemStackRequestSlotInfo()

    def write(self, stream: BinaryStream) -> None:
        self.source.write(stream)
        self.destination.write(stream)

    @classmethod
    def read(cls, stream: ReadOnlyBinaryStream) -> Self:
        action = cls()
        action.source.read(stream)
        action.destination.read(stream)
        return action


class DropAction(ItemStackRequestAction):
    amount: int
    source: ItemStackRequestSlotInfo
    randomly: bool

    def __init__(
        self,
        amount: int = 0,
        source: Optional[ItemStackRequestSlotInfo] = None,
        randomly: bool = False,
    ):
        super().__init__(ItemStackRequestActionType.Drop)
        self.amount = amount
        self.source = source or ItemStackRequestSlotInfo()
        self.randomly = randomly

    def write(self, stream: BinaryStream) -> None:
        stream.write_byte(self.amount)
        self.source.write(stream)
        stream.write_bool(self.randomly)

    @classmethod
    def read(cls, stream: ReadOnlyBinaryStream) -> Self:
        action = cls()
        action.amount = stream.get_byte()
        action.source.read(stream)
        action.randomly = stream.get_bool()
        return action


class ItemStackRequestData:
    client_request_id: int
    strings_to_filter: List[bytes]
    strings_to_filter_origin: int
    actions: List[ItemStackRequestAction]
    _request_buffer: bytes
    _read_position: int

    def __init__(
        self,
        client_request_id: int = 0,
        strings_to_filter: Optional[List[bytes]] = None,
        strings_to_filter_origin: int = 0,
        actions: Optional[List[ItemStackRequestAction]] = None,
        is_parsable_action: bool = False,
        request_buffer: bytes = b"",
        read_position: int = 0,
    ):
        self.client_request_id = client_request_id
        self.strings_to_filter = strings_to_filter or []
        self.strings_to_filter_origin = strings_to_filter_origin
        self.actions = actions or []
        self.is_parsable_action = is_parsable_action
        self._request_buffer = request_buffer
        self._read_position = read_position

    @staticmethod
    def read_action(
        stream: ReadOnlyBinaryStream, type: int
    ) -> ItemStackRequestAction | None:
        match type:
            case ItemStackRequestActionType.Take:
                return TakeAction.read(stream)
            case ItemStackRequestActionType.Place:
                return PlaceAction.read(stream)
            case ItemStackRequestActionType.Swap:
                return SwapAction.read(stream)
            case ItemStackRequestActionType.Drop:
                return DropAction.read(stream)
            case _:
                return None

    def write(self, stream: BinaryStream) -> None:
        if self.is_parsable_action:
            stream.write_varint(self.client_request_id)
            stream.write_unsigned_varint(len(self.actions))
            for action in self.actions:
                stream.write_unsigned_varint(action.type)
                stream.write_byte(action.type)
                action.write(stream)
            stream.write_unsigned_varint(len(self.strings_to_filter))
            for stf in self.strings_to_filter:
                stream.write_bytes(stf)
            stream.write_signed_int(self.strings_to_filter_origin)
        else:
            stream.write_raw_bytes(self._request_buffer)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        self.is_parsable_action = True
        self._read_position = stream.get_position()
        self.client_request_id = stream.get_varint()
        actions_len = stream.get_unsigned_varint()
        for _ in range(actions_len):
            type_id = stream.get_unsigned_varint()
            inner_type_id = stream.get_byte()
            action = self.read_action(stream, type_id)
            if action is not None:
                self.actions.append(action)
            else:
                self.is_parsable_action = False
                break
        if self.is_parsable_action:
            stf_len = stream.get_unsigned_varint()
            for _ in range(stf_len):
                self.strings_to_filter.append(stream.get_bytes())
            self.strings_to_filter_origin = stream.get_signed_int()
        else:
            stream.set_position(self._read_position)
            self._request_buffer = stream.get_left_buffer()
