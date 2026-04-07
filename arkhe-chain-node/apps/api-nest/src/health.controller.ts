import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';

@ApiTags('health')
@Controller('health')
export class HealthController {
  @Get()
  @ApiOperation({ summary: 'Status Check da API' })
  check() {
    return { status: 'OPERATIONAL', timestamp: new Date().toISOString() };
  }
}
