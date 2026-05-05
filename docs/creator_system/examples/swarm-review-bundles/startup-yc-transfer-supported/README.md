# Startup YC Transfer-Supported Review Bundle

This example shows how to package an existing creator run for Spark Swarm
review without publishing it to the network.

It points at `docs/creator_system/examples/startup-yc-creator-run`, which is a
curated `transfer_supported` fixture with a schema-valid local Swarm
contribution packet.

The bundle is intentionally local:

- `network_absorbable=false`
- `network_publication_allowed=false`
- product runtime controls remain read-only
- mission status is marked absent because this historical fixture predates the
  saved mission-status packet

Validate this example through `tests/test_creator_system_docs.py`.
