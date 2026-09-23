# Copyright © 2025 GlacieTeam. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# SPDX-License-Identifier: MPL-2.0

from typing import List, Optional

from bstream import BinaryStream, ReadOnlyBinaryStream

from bedrock_protocol.packets.types.full_container_name import FullContainerName
from bedrock_protocol.serializer.common_types import read_list, write_list, \
    read_optional, write_optional


class ItemStackResponseSlotInfo:
    slot: int
    hotbar_slot: int
    count: int
    item_stack_id: int | None
    custom_name: str
    filtered_custom_name: str | None
    durability_correction: int

    def __init__(
        self,
        slot: int = 0,
        hotbar_slot: int = 0,
        count: int = 0,
        item_stack_id: int | None = None,
        custom_name: str = "",
        filtered_custom_name: str | None = None,
        durability_correction: int = 0,
    ):
        self.slot = slot
        self.hotbar_slot = hotbar_slot
        self.count = count
        self.item_stack_id = item_stack_id
        self.custom_name = custom_name
        self.filtered_custom_name = filtered_custom_name
        self.durability_correction = durability_correction

    def write(self, stream: BinaryStream) -> None:
        stream.write_byte(self.slot)
        stream.write_byte(self.hotbar_slot)
        stream.write_byte(self.count)
        write_optional(
            stream,
            self.item_stack_id,
            lambda s, v: s.write_varint(v)
        )
        stream.write_string(self.custom_name)
        write_optional(stream, self.filtered_custom_name, lambda s, v: s.write_string(v))
        stream.write_varint(self.durability_correction)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        self.slot = stream.get_byte()
        self.hotbar_slot = stream.get_byte()
        self.count = stream.get_byte()
        self.item_stack_id = read_optional(
            stream,
            lambda s: s.get_varint()
        )
        self.custom_name = stream.get_string()
        self.filtered_custom_name = read_optional(stream, lambda s: s.get_string())
        self.durability_correction = stream.get_varint()


class ItemStackResponseContainerInfo:
    container: FullContainerName
    slots: List[ItemStackResponseSlotInfo]

    def __init__(
        self,
        container: Optional[FullContainerName] = None,
        slots: List[ItemStackResponseSlotInfo] | None = None,
    ):
        self.container = container or FullContainerName()
        self.slots = slots or []

    def write(self, stream: BinaryStream) -> None:
        self.container.write(stream)
        stream.write_unsigned_varint(len(self.slots))
        for slot in self.slots:
            slot.write(stream)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        self.container = FullContainerName()
        self.container.read(stream)
        count = stream.get_unsigned_varint()
        self.slots = []
        for _ in range(count):
            slot = ItemStackResponseSlotInfo()
            slot.read(stream)
            self.slots.append(slot)


class ItemStackResponse:
    result: int
    request_id: int
    container_infos: List[ItemStackResponseContainerInfo] | None

    RESULT_OK = 0
    RESULT_ERROR = 1

    def __init__(self,
        result: int = RESULT_OK,
        request_id: int = 0,
        container_infos: List[ItemStackResponseContainerInfo] | None = None
    ):
        self.result = result
        self.request_id = request_id
        self.container_infos = container_infos or None

    def write(self, stream: BinaryStream) -> None:
        stream.write_byte(self.result)
        stream.write_varint(self.request_id)
        write_optional(
            stream,
            self.container_infos,
            lambda out, container_infos: write_list(out, container_infos, lambda o, v: v.write(o))
        )

    @staticmethod
    def read_container(stream: ReadOnlyBinaryStream) -> ItemStackResponseContainerInfo:
        container_info = ItemStackResponseContainerInfo()
        container_info.read(stream)
        return container_info

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        self.result = stream.get_byte()
        self.request_id = stream.get_varint()
        self.container_infos = read_optional(
            stream,
            lambda s: read_list(s, self.read_container)
        )
