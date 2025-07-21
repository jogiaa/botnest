import asyncio
from pathlib import Path
from typing import Optional, Callable, AsyncGenerator, Union, List
from dataclasses import dataclass
import fnmatch


# --- Sealed Class Equivalents ---
class FileResult: pass


@dataclass
class FileDetails(FileResult):
    path: str
    size: int
    content: str


@dataclass
class FileError(FileResult):
    error: Exception


class AsyncFileProcessor:
    def __init__(
            self,
            source_str: str,
            dest_str: Optional[str] = None,
            file_filter: Optional[List[str]] = None,
            overwrite: bool = True
    ):
        self.source = Path(source_str).resolve()
        self.destination = Path(dest_str).resolve() if dest_str else None
        self.file_filter = file_filter
        self.overwrite = overwrite

    def _is_ignored(self, path: Path) -> bool:
        rel_path = str(path.relative_to(self.source)) if self.source.is_dir() else str(path.name)
        return any(fnmatch.fnmatch(rel_path, pattern) for pattern in self.file_filter)

    async def stream_files(self) -> AsyncGenerator[FileResult, None]:
        """Yields FileDetails for each matching file (optionally filtered)"""
        print(f"🗃️ Scanning:")
        if self.source.is_file():
            print(f"👀 Scanning: {self.source}")
            if not self._is_ignored(self.source):
                yield await self._read_file(self.source)
            else:
                print(f"🙈Ignoring : {self.source}")
        elif self.source.is_dir():
            for file in self.source.rglob("*"):
                print(f"👀 Scanning: {file}")
                if file.is_file():
                    if self._is_ignored(file):
                        print(f"🙈Ignoring : {file}")
                        continue
                    else:
                        print(f"🚶🏽Going to read : {file}")
                        yield await self._read_file(file)
        else:
            yield FileError(error=FileNotFoundError(f"Source '{self.source}' not found"))

    async def _read_file(self, file: Path) -> FileResult:
        print(f"📖 Reading: {file}")
        try:
            content = await asyncio.to_thread(file.read_text, encoding='utf-8')
            return FileDetails(path=str(file), size=file.stat().st_size, content=content)
        except Exception as e:
            return FileError(error=e)

    async def save_file(self, result: FileDetails) -> FileResult:
        print(f"📝 Saving: {result}")
        try:
            src_path = Path(result.path)
            if self.destination:
                # relative = src_path.relative_to(self.source) if self.source.is_dir() else Path(src_path.name)
                # target = self.destination / relative
                if self.source.is_file():
                    # If source is a file:
                    if self.destination.is_dir():
                        target = self.destination / src_path.name
                    else:
                        target = self.destination
                else:
                    # Source is a directory — preserve subpath
                    relative = src_path.relative_to(self.source)
                    target = self.destination / relative
            else:
                target = src_path

            if target.exists() and not self.overwrite:
                print(f"⚠️ Skipped (exists): {target}")
                return FileResult()  # Or return something like FileSkipped if needed

            await asyncio.to_thread(target.parent.mkdir, parents=True, exist_ok=True)
            await asyncio.to_thread(target.write_text, result.content, encoding='utf-8')
            return FileResult()
        except Exception as e:
            return FileError(error=e)


async def main():
    source = "koin/examples/coffee-maker/src/main/kotlin/org/koin/example/CoffeeApp.kt"
    destination = "koin/examples/coffee-maker/src/main/kotlin/org/koin/example/CoffeeApp2.kt"
    processor = AsyncFileProcessor(
        source_str=source,
        dest_str=destination,
        file_filter=["*.sh", "*.gradle", "temp/*", "*~"],
        overwrite=True
    )

    async for file in processor.stream_files():
        if isinstance(file, FileDetails):
            print(f" {file.path}")
            file.content = file.content.upper()
            result = await processor.save_file(file)
            if isinstance(result, FileError):
                print(f"❌ Save failed: {result.error}")
        elif isinstance(file, FileError):
            print(f"❌ Read failed: {file.error}")


if __name__ == "__main__":
    asyncio.run(main())
