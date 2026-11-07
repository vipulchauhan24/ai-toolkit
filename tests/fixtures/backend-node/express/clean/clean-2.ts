export interface Clock {
  now(): Date;
}

export class ReportService {
  constructor(private readonly clock: Clock) {}

  label(name: string): string {
    return `${name} at ${this.clock.now().toISOString()}`;
  }
}
