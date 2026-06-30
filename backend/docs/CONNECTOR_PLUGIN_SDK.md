# Connector Plugin SDK

## Plugin Contract
A connector plugin must:
1. Inherit from BaseConnector.
2. Implement all required connector operations.
3. Provide register_plugins(registry) in the plugin module.
4. Register at least one ConnectorSpec.

## Registration Function
A plugin module should expose:

- register_plugins(registry): registers ConnectorSpec + builder.

The loader discovers this function from:
- Package modules
- Python files by path
- Python entry points group: tkk_uv.connectors

## Builder Signature
The registry builder receives:
- spec: ConnectorSpec
- config: dict

And returns a BaseConnector instance.

## Runtime Config
Runtime configuration can override default plugin config through ConnectorFactory.create_connector(key, runtime_config).

## Best Practices
- Keep connector auth and I/O concerns inside plugin class.
- Keep plugin module self-contained with minimal side effects.
- Emit structured metrics and logs from connector methods.
- Use registry keys with stable prefixes, for example db.postgresql or cloud.s3.
