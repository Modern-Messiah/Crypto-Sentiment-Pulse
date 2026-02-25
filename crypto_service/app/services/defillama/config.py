import httpx

DEFILLAMA_API_BASE = "https://api.llama.fi"
DEFILLAMA_CHANS_URL = f"{DEFILLAMA_API_BASE}/chains"
DEFILLAMA_STABLES_URL = "https://stablecoins.llama.fi/stablecoinchains"
DEFILLAMA_PROTOCOLS_URL = f"{DEFILLAMA_API_BASE}/protocols"

HISTORY_SLUG_OVERRIDES = {
    "Binance": "BSC",
    "Ripple": "XRPL",
    "Cosmos": "CosmosHub",
    "Near": "near",
    "Optimism": "Optimism",
    "Avalanche": "Avalanche"
}

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://defillama.com/",
    "Origin": "https://defillama.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Sec-Ch-Ua": '"Chromium";v="145", "Google Chrome";v="145", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Linux"',
}


def create_client(timeout: float = 15.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=timeout,
        headers=BROWSER_HEADERS,
        http2=True,
        follow_redirects=True,
    )
