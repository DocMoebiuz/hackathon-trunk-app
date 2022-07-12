#! /bin/sh
docker run --name trunkservice --net=host -e DAPR_GRPC_PORT=$DAPR_GRPC_PORT -e VEHICLEDATABROKER_DAPR_APP_ID=vehicledatabroker trunkservice