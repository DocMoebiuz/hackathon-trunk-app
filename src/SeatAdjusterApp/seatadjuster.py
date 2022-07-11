# Copyright (c) 2022 Robert Bosch GmbH and Microsoft Corporation
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""A sample Velocitas vehicle app for adjusting seat position."""

# pylint: disable=C0103, C0413, E1101

import asyncio
import json
import logging
import signal

# import grpc
from sdv.util.log import (  # type: ignore
    get_opentelemetry_log_factory,
    get_opentelemetry_log_format,
)
from sdv.vehicle_app import VehicleApp, subscribe_topic
from sdv_model import Vehicle, vehicle  # type: ignore
from sdv_model.proto.trunk_pb2 import REAR

logging.setLogRecordFactory(get_opentelemetry_log_factory())
logging.basicConfig(format=get_opentelemetry_log_format())
logging.getLogger().setLevel("INFO")
logger = logging.getLogger(__name__)


class SeatAdjusterApp(VehicleApp):
    """
    Sample Velocitas Vehicle App.

    The SeatAdjusterApp subscribes to a MQTT topic to listen for incoming
    requests to change the seat position and calls the SeatService to move the seat
    upon such a request, but only if Vehicle.Speed equals 0.

    It also subcribes to the VehicleDataBroker for updates of the
    Vehicle.Cabin.Seat.Row1.Pos1.Position signal and publishes this
    information via another specific MQTT topic
    """

    def __init__(self, vehicle_client: Vehicle):
        super().__init__()
        self.Vehicle = vehicle_client

    async def on_start(self):
        """Run when the vehicle app starts"""
        try:
            await self.Vehicle.Body.Trunk.element_at("Rear").IsOpen.subscribe(
                self.on_trunk_state_changed
            )
        except Exception as e:
            logger.error(e)

    async def on_trunk_state_changed(self, data):
        response_topic = "deliveryapp/trunkState"
        trunk_path = self.Vehicle.Body.Trunk.element_at("Rear").IsOpen.get_path()
        await self.publish_mqtt_event(
            response_topic,
            json.dumps({"isOpen": data.fields[trunk_path].bool_value}),
        )

    @subscribe_topic("deliveryapp/openTrunk/request")
    async def on_open_trunk_request_received(self, data_str: str) -> None:
        data = json.loads(data_str)
        response_topic = "deliveryapp/openTrunk/response"
        response_data = {"requestId": data["requestId"], "result": {}}

        try:
            is_open = await self.Vehicle.Body.Trunk.element_at("Rear").IsOpen.get()

            if is_open:
                await self.Vehicle.Body.TrunkService.Close(REAR)
                response_data["result"] = {
                    "status": 0,
                    "message": "Trunk will now close",
                }
            else:
                await self.Vehicle.Body.TrunkService.Open(REAR)
                response_data["result"] = {
                    "status": 0,
                    "message": "Trunk will now open",
                }

        except Exception as e:
            response_data["result"] = {
                "status": 1,
                "message": e,
            }

        await self.publish_mqtt_event(response_topic, json.dumps(response_data))


async def main():

    """Main function"""
    logger.info("Starting seat adjuster app...")
    seat_adjuster_app = SeatAdjusterApp(vehicle)
    await seat_adjuster_app.run()


LOOP = asyncio.get_event_loop()
LOOP.add_signal_handler(signal.SIGTERM, LOOP.stop)
LOOP.run_until_complete(main())
LOOP.close()
