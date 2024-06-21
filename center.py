import asyncio
import main
import add_missing_data
import validation

async def main_routine():
    frame_queue = await main.process_video()
    print(frame_queue)
    frame_queue = await add_missing_data.interpolated_data(frame_queue)
    frame_queue = await add_missing_data.merge_rows(frame_queue)
    await validation.validation(frame_queue)


if __name__ == "__main__":
    asyncio.run(main_routine())


