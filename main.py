import asyncio
from chess_game import ChessGame

async def main():
    game = ChessGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
