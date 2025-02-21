from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler, MemoryAdaptiveDispatcher, CrawlerMonitor, DisplayMode, RateLimiter

async def crawl_batch(urls):
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False,  # Default: get all results at once,
        check_robots_txt=True,
    )

    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=3.0,
        max_session_permit=20,
        rate_limiter=RateLimiter(
            base_delay=(1.0, 2.0),
            max_delay=60.0,
            max_retries=2
        ),
        monitor=CrawlerMonitor(
            display_mode=DisplayMode.DETAILED,
            max_visible_rows=25
        )
    )

    async with AsyncWebCrawler( config=browser_config) as crawler:
        # Get all results at once
        
        results = await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        )

        # Process all results after completion
        for result in results:
            if result.success:
                print(result.url)
                print(len(result.markdown))
                print("="*50)
                output.append({
                    "url": result.url,
                    "markdown": result.markdown,
                    "word_count": len(result.markdown.split())
                })
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")

path = "final_html_links.json"
with open(path, "r") as f:
    data = json.load(f)

output = []
asyncio.run(crawl_batch(data))

with open("final_output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)