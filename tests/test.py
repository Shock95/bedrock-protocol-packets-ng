# Copyright © 2025 GlacieTeam. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# SPDX-License-Identifier: MPL-2.0
from enum import Enum
from typing import Any, cast

from bstream._bstream import BinaryStream
from endstone_inventoryui.network.container_ui_ids import ContainerUIIds

from bedrock_protocol.packets.enums import ItemStackRequestActionType
from bedrock_protocol.packets.packet import *  # pylint: disable=wildcard-import,unused-wildcard-import
from bedrock_protocol.packets.types import *  # pylint: disable=wildcard-import,unused-wildcard-import
from bedrock_protocol.packets import *  # pylint: disable=wildcard-import,unused-wildcard-import
from bedrock_protocol.packets.types.item_stack_request import TakeAction


def test1():
    packet_write = UpdateBlockPacket(BlockPos(11, 45, 14), 2537812, 3, 0)
    payload = packet_write.serialize()
    print(f"{payload.hex()} | {payload.hex()=='162d1cd4f29a010300'}")

    packet_read = UpdateBlockPacket()
    packet_read.deserialize(bytes.fromhex("162d1cd4f29a010300"))
    print(f"{packet_read.block_position.x} | {packet_read.block_position.x==11}")
    print(f"{packet_read.block_position.y} | {packet_read.block_position.y==45}")
    print(f"{packet_read.block_position.z} | {packet_read.block_position.z==14}")
    print(f"{packet_read.block_runtime_id} | {packet_read.block_runtime_id==2537812}")
    print(f"{packet_read.update_flag} | {packet_read.update_flag==3}")
    print(f"{packet_read.block_layer} | {packet_read.block_layer==0}")


def test2():
    """Test default constructor"""
    for packet_id in MinecraftPacketIds:
        packet = MinecraftPackets.create_packet(packet_id)
        if packet.get_packet_name() != "UnimplementedPacket":
            data = packet.serialize()
            packet.deserialize(data)
            status = data == packet.serialize()
            print(f"{packet.get_packet_name()} : {status}")
            if not status:
                raise RuntimeError("Packet test failed")
    print("All packets default constructor test pass")  # if no exception


def test_item_stack_request():
    # ItemStackRequest payload: item taken from chest to cursor inventory (slot 0)
    payload = b"\x01\xd5\x03\x01\x00\x00\x01\x07\x00\x00\x01\x00\x00\x00;\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff"
    pk = ItemStackRequestPacket()
    pk.deserialize(payload)

    assert len(pk.request.request_data) == 1
    request_data = pk.request.request_data[0]

    assert len(request_data.actions) == 1
    request_action = request_data.actions[0]

    assert request_action.type == ItemStackRequestActionType.Take
    request_action = cast(TakeAction, request_action)

    assert request_action.source.container.container_enum == ContainerUIIds.LEVEL_ENTITY
    assert request_action.destination.container.container_enum == ContainerUIIds.CURSOR

    print("ItemStackRequest test passed")

if __name__ == "__main__":
    print("-" * 25, "Test1", "-" * 25)
    test1()
    print("-" * 25, "Test2", "-" * 25)
    test2()
    print("-" * 25, "Test3", "-" * 25)
    test_item_stack_request()
    print("-" * 25, "END", "-" * 25)
