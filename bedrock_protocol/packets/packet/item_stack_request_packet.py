# Copyright © 2025 GlacieTeam. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# SPDX-License-Identifier: MPL-2.0

from typing import Optional, List
from bstream import BinaryStream, ReadOnlyBinaryStream
from bedrock_protocol.packets.minecraft_packet_ids import MinecraftPacketIds
from bedrock_protocol.packets.packet.packet_base import Packet
from bedrock_protocol.packets.types.item_stack_request import ItemStackRequestData


class ItemStackRequestPacket(Packet):

    requests: List[ItemStackRequestData]

    def __init__(self, requests: Optional[List[ItemStackRequestData]] = None):
        super().__init__()
        self.requests = requests or []

    def get_packet_id(self) -> MinecraftPacketIds:
        return MinecraftPacketIds.ItemStackRequest

    def get_packet_name(self) -> str:
        return "ItemStackRequest"

    def write(self, stream: BinaryStream) -> None:
        stream.write_unsigned_varint(len(self.requests))
        for request in self.requests:
            request.write(stream)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        length = stream.get_unsigned_varint()
        for _ in range(length):
            data = ItemStackRequestData()
            data.read(stream)
            self.requests.append(data)
