// packages/lucent-sdk/src/connectors/ConnectorFactory.ts
import { LucentCollector } from '../LucentCollector';
import { BaseConnector, ConnectorConfig } from './BaseConnector';
import { PostHogConnector } from './PostHogConnector';
import { FullStoryConnector } from './FullStoryConnector';

// Factory para instanciar conectores
export class ConnectorFactory {
  static create(
    type: 'posthog' | 'fullstory' | 'amplitude',
    config: ConnectorConfig,
    lucent: LucentCollector
  ): BaseConnector {
    switch(type) {
      case 'posthog': return new PostHogConnector(config, lucent);
      case 'fullstory': return new FullStoryConnector(config, lucent);
      default: throw new Error(`Connector ${type} not implemented`);
    }
  }
}
