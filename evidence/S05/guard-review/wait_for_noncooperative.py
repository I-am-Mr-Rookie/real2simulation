# Reviewer-only repro: asyncio.wait_for does not bound a non-cooperative awaitable.
# Run ONLY under a parent hard timeout (reviewer used Start-Process + WaitForExit(10000)).
import asyncio,time
async def stubborn():
    try: await asyncio.sleep(5)
    except asyncio.CancelledError:
        await asyncio.sleep(2)  # swallows cancel, keeps running
        return 'late'
async def m():
    t=time.monotonic()
    try: r=await asyncio.wait_for(stubborn(),timeout=0.2); print('returned',r)
    except Exception as e: print(type(e).__name__)
    print('elapsed',round(time.monotonic()-t,2))
asyncio.run(m())
