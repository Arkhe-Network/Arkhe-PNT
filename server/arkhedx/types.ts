export type Side = 'buy' | 'sell';
export type OrderType = 'limit' | 'market';

export interface Order {
  id: string;
  trader: string;
  side: Side;
  type: OrderType;
  price: number;
  size: number;
  filled: number;
  timestamp: number;
  janusLocked: boolean;
}

export interface Trade {
  id: string;
  makerOrderId: string;
  takerOrderId: string;
  price: number;
  size: number;
  timestamp: number;
  makerFee: number;
  takerFee: number;
}
