"""Load testing script for Web Intelligence Platform"""
import asyncio
import httpx
import time
import statistics
from typing import List
import random
import string

API_BASE_URL = "http://localhost:8000/api/v1"

async def test_create_site(client: httpx.AsyncClient, num: int) -> dict:
    """Create a test site"""
    domain = f"test-site-{num}-{random.randint(1000, 9999)}.com"
    try:
        start = time.time()
        response = await client.post(
            f"{API_BASE_URL}/sites",
            json={"domain": domain, "business_value_score": random.random()},
            timeout=10
        )
        elapsed = time.time() - start
        return {
            "success": response.status_code == 201,
            "elapsed": elapsed,
            "status_code": response.status_code,
            "site_id": response.json().get("site_id") if response.status_code == 201 else None
        }
    except Exception as e:
        return {
            "success": False,
            "elapsed": 0,
            "error": str(e),
            "status_code": 0
        }

async def test_list_sites(client: httpx.AsyncClient) -> dict:
    """List sites"""
    try:
        start = time.time()
        response = await client.get(
            f"{API_BASE_URL}/sites?limit=50",
            timeout=10
        )
        elapsed = time.time() - start
        return {
            "success": response.status_code == 200,
            "elapsed": elapsed,
            "status_code": response.status_code
        }
    except Exception as e:
        return {
            "success": False,
            "elapsed": 0,
            "error": str(e),
            "status_code": 0
        }

async def test_health(client: httpx.AsyncClient) -> dict:
    """Test health endpoint"""
    try:
        start = time.time()
        response = await client.get(
            "http://localhost:8000/health",
            timeout=5
        )
        elapsed = time.time() - start
        return {
            "success": response.status_code == 200,
            "elapsed": elapsed,
            "status_code": response.status_code
        }
    except Exception as e:
        return {
            "success": False,
            "elapsed": 0,
            "error": str(e),
            "status_code": 0
        }

async def run_load_test(num_concurrent: int = 10, num_requests_per_client: int = 20):
    """Run load test"""
    print(f"\n🔥 Starting Load Test")
    print(f"   Concurrent clients: {num_concurrent}")
    print(f"   Requests per client: {num_requests_per_client}")
    print(f"   Total requests: {num_concurrent * num_requests_per_client}\n")
    
    async with httpx.AsyncClient() as client:
        # Test health first
        print("📊 Testing health endpoint...")
        health_result = await test_health(client)
        print(f"   Health: {'✅' if health_result['success'] else '❌'} ({health_result['elapsed']:.2f}s)\n")
        
        # Test listing sites
        print("📋 Testing list sites...")
        list_result = await test_list_sites(client)
        print(f"   List: {'✅' if list_result['success'] else '❌'} ({list_result['elapsed']:.2f}s)\n")
        
        # Create sites load test
        print(f"🌍 Load testing create sites ({num_concurrent}x{num_requests_per_client} requests)...")
        create_times: List[float] = []
        create_successes = 0
        
        start_time = time.time()
        
        for batch in range(num_requests_per_client):
            tasks = [test_create_site(client, i) for i in range(num_concurrent)]
            results = await asyncio.gather(*tasks)
            
            for result in results:
                if result["success"]:
                    create_successes += 1
                    create_times.append(result["elapsed"])
                else:
                    print(f"   ❌ Failed: {result.get('error', 'Unknown')}")
            
            # Progress indicator
            if (batch + 1) % 5 == 0:
                print(f"   Completed {(batch + 1) * num_concurrent} requests...")
        
        total_time = time.time() - start_time
        
        # Calculate stats
        print(f"\n✅ Results:")
        print(f"   Total requests: {num_concurrent * num_requests_per_client}")
        print(f"   Successful: {create_successes}")
        print(f"   Failed: {num_concurrent * num_requests_per_client - create_successes}")
        print(f"   Success rate: {(create_successes / (num_concurrent * num_requests_per_client) * 100):.1f}%")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Throughput: {(num_concurrent * num_requests_per_client) / total_time:.1f} req/s")
        
        if create_times:
            print(f"\n⏱️  Response times:")
            print(f"   Min: {min(create_times):.3f}s")
            print(f"   Max: {max(create_times):.3f}s")
            print(f"   Avg: {statistics.mean(create_times):.3f}s")
            print(f"   Median: {statistics.median(create_times):.3f}s")
            print(f"   StdDev: {statistics.stdev(create_times):.3f}s" if len(create_times) > 1 else "   StdDev: N/A")
            
            # Percentiles
            sorted_times = sorted(create_times)
            p50 = sorted_times[int(len(sorted_times) * 0.50)]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
            
            print(f"\n📈 Percentiles:")
            print(f"   p50: {p50:.3f}s")
            print(f"   p95: {p95:.3f}s")
            print(f"   p99: {p99:.3f}s")

if __name__ == "__main__":
    print("=" * 60)
    print("Web Intelligence Platform - Load Test")
    print("=" * 60)
    print("\n⚠️  Make sure docker-compose is running:")
    print("   docker-compose up --build\n")
    
    # Run test with different concurrency levels
    try:
        # Small load test
        asyncio.run(run_load_test(num_concurrent=5, num_requests_per_client=10))
        
        # Medium load test
        asyncio.run(run_load_test(num_concurrent=10, num_requests_per_client=20))
        
        # Larger load test
        asyncio.run(run_load_test(num_concurrent=20, num_requests_per_client=10))
        
        print("\n" + "=" * 60)
        print("✅ Load test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Load test failed: {e}")

