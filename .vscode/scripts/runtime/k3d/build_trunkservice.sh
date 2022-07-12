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

ROOT_DIRECTORY=$( realpath "$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../../../.." )
PATH_DOCKERFILE="tools/kuksa.val.services/trunk_service/Dockerfile"
PROJECT_NAME="trunkservice"
TRUKSERVICE_TAG=$(cat $ROOT_DIRECTORY/prerequisite_settings.json | jq .trunkservice.version | tr -d '"')

BUILD_ARGS=

if [ -n "$HTTP_PROXY" ]; then
    echo "Building image without proxy configuration"

    BUILD_ARGS=--build-arg HTTP_PROXY="$HTTP_PROXY" \
    --build-arg HTTPS_PROXY="$HTTPS_PROXY" \
    --build-arg FTP_PROXY="$FTP_PROXY" \
    --build-arg ALL_PROXY="$ALL_PROXY" \
    --build-arg NO_PROXY="$NO_PROXY"
fi

cd $ROOT_DIRECTORY/tools/kuksa.val.services/trunk_service
DOCKER_BUILDKIT=1 docker build --progress=plain -t localhost:12345/$PROJECT_NAME:$TRUKSERVICE_TAG . --no-cache $BUILD_ARGS
docker push localhost:12345/$PROJECT_NAME:$TRUKSERVICE_TAG