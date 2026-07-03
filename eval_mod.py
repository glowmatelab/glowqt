import io
import uuid
import asyncio
import traceback
from html import escape
from typing import Any
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def meval(code: str, globs: dict, **kwargs) -> Any:
    """Evaluates code as an expression, or executes it as a statement
    block if it's not a single valid expression."""
    globs = {**globs, **kwargs}
    try:
        compiled = compile(code, "<string>", "eval")
        result = eval(compiled, globs)
        if hasattr(result, "__await__"):
            result = await result
        return result
    except SyntaxError:
        pass

    async def __ex():
        locs = {}
        exec(
            "async def __func():\n"
            + "\n".join(f"    {l}" for l in code.split("\n")),
            globs,
            locs,
        )
        return await locs["__func"]()
    return await __ex()

def format_exception(e: Exception, tb) -> str:
    return "".join(traceback.format_exception(type(e), e, None if not tb else e.__traceback__))

def setup_eval(app, OWNER_ID, active_chats, load_data, save_data):
    """Is function se saare variables main.py se is file me connect ho jayenge"""
    
    @app.on_message(filters.command(["eval", "exec"]) & filters.user(OWNER_ID))
    async def eval_handler(client, message):
        try:
            await message.delete()
        except Exception:
            pass

        if len(message.command) < 2:
            return await message.reply_text("❌ Usage: `/eval <code>`")

        code = message.text.split(None, 1)[1]
        out_buf = io.StringIO()

        async def send(*args: Any, **kwargs: Any):
            return await message.reply_text(*args, **kwargs)

        def _print(*args: Any, **kwargs: Any) -> None:
            kwargs.setdefault("file", out_buf)
            print(*args, **kwargs)

        # Jo bhi variables tum eval ke andar test karna chahte ho unhe yahan daal do
        eval_vars = {
            "m": message,
            "r": message.reply_to_message,
            "chat": message.chat,
            "user": message.from_user,
            "app": app,
            "client": client,
            "ikb": InlineKeyboardButton,
            "ikm": InlineKeyboardMarkup,
            "send": send,
            "print": _print,
            "active_chats": active_chats,
            "load_data": load_data,
            "save_data": save_data,
        }

        try:
            result = await meval(code, globals(), **eval_vars)
            if result is not None or not out_buf.getvalue():
                print(result, file=out_buf)
            prefix = ""
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            snippet_tb = next((i for i, f in enumerate(tb) if f.filename == "<string>"), -1)
            formatted_tb = format_exception(e, tb[snippet_tb:] if snippet_tb != -1 else tb)
            print(formatted_tb, file=out_buf)
            prefix = "❌ **Error:**\n"

        output = out_buf.getvalue().strip()
        response = f"{prefix}```\n{escape(output)}\n```"

        if len(response) > 4096:
            with io.BytesIO(output.encode()) as out_file:
                out_file.name = f"{uuid.uuid4().hex[:8].lower()}.txt"
                return await message.reply_document(document=out_file, disable_notification=True)

        await message.reply_text(response)
