import logging

logger = logging.getLogger(__name__)

class BinanceProcessorMixin:

    async def process_message(self, data: dict):
        try:
            if 'result' in data:
                logger.info("Binance subscription confirmed")
                return

            event_type = data.get('e')

            if event_type == '24hrTicker':
                symbol = data.get('s')
                if symbol:
                    price = float(data.get('c', 0))
                    timestamp = data.get('E')

                    self.history[symbol].append({
                        'time': timestamp,
                        'price': price
                    })

                    history_prices = [p['price'] for p in self.history[symbol]]
                    history_times = [p['time'] for p in self.history[symbol]]

                    if not history_prices:
                        rsi = 50.0
                    else:
                        minute_closes = []
                        seen_minutes = set()

                        for t, p in zip(reversed(history_times), reversed(history_prices)):
                            minute_key = int(t / 60000)
                            if minute_key not in seen_minutes:
                                minute_closes.append(p)
                                seen_minutes.add(minute_key)
                                if len(minute_closes) >= 15:
                                    break

                        minute_closes.reverse()

                        if len(minute_closes) < 15 and len(history_prices) > 20:
                            sample_prices = history_prices[::5]
                            rsi = self.calculate_rsi(sample_prices, period=14)
                        elif len(minute_closes) >= 15:
                            rsi = self.calculate_rsi(minute_closes, period=14)
                        else:
                            rsi = 50.0

                    is_trending = False
                    tvl_info = self.tvl_data.get(symbol, {})
                    cg_id = tvl_info.get('cg_id')
                    rank = tvl_info.get('rank')
                    
                    # Mark as trending if it's in trending list OR in top 15 by market cap 
                    # (CoinGecko search UI usually shows both)
                    if rank and rank <= 15:
                        is_trending = True
                    else:
                        for trending in self.trending_symbols:
                            if trending in symbol or (cg_id and trending == cg_id):
                                is_trending = True
                                break

                    tvl_info = self.tvl_data.get(symbol)
                    
                    self.prices[symbol] = {
                        'symbol': symbol,
                        'price': price,
                        'change_24h': float(data.get('P', 0)),
                        'volume_24h': float(data.get('v', 0)),
                        'high_24h': float(data.get('h', 0)),
                        'low_24h': float(data.get('l', 0)),
                        'timestamp': timestamp,
                        'rsi': rsi,
                        'is_trending': is_trending,
                        'tvl': tvl_info.get('tvl') if tvl_info else None,
                        'tvl_change_1d': tvl_info.get('change_1d') if tvl_info else None,
                        'money_flow_24h': None, # No longer from CoinGecko markets
                        'global_stats': self.global_stats
                    }

        except Exception as e:
            logger.error(f"Error processing Binance data: {e}")

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50.0

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        recent_gains = gains[-period:]
        recent_losses = losses[-period:]

        avg_gain = sum(recent_gains) / period
        avg_loss = sum(recent_losses) / period

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 1)
