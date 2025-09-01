import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Generator, List

from poc_agno.utils import Logger, get_builtin_logger


# --- Sealed Class Equivalents ---
class FileResult: pass


@dataclass
class FileDetails(FileResult):
    path: str
    rel_path: str
    content: str


@dataclass
class FileError(FileResult):
    path: str
    error: Exception


class AnotherFileProcessor:
    def __init__(
            self,
            source_str: str,
            dest_str: Optional[str] = None,
            file_filter: Optional[List[str]] = None,
            ignored_directories: Optional[List[str]] = None,
            overwrite: bool = True,
            logger: Optional[Logger] = None
    ):
        self.source = Path(source_str).resolve()
        self.destination = Path(dest_str).resolve() if dest_str else None
        self.file_filter = file_filter if file_filter is not None else ["*.sh", "*.gradle", "temp/*", "*~",
                                                                        "*.DS_Store"]
        self.ignored_directories = ignored_directories if ignored_directories is not None else ["venv", "test", ".git"]
        self.overwrite = overwrite
        self.logger = logger if logger is not None else get_builtin_logger()
        self.base_path = Path(self.source)

    def _is_ignored(self, path: Path) -> bool:
        rel_path = str(path.relative_to(self.source)) if self.source.is_dir() else str(path.name)
        return any(fnmatch.fnmatch(rel_path, pattern) for pattern in self.file_filter)

    def stream_files(self) -> Generator[FileResult, None, None]:
        if self.source.is_file():
            self.logger.debug(f"👀 Scanning: {self.source}")
            if not self._is_ignored(self.source):
                yield self._read_file(self.source)
            else:
                self.logger.debug(f"🙈 Ignoring: {self.source}")
        elif self.source.is_dir():
            for file in self.source.rglob("*"):
                self.logger.debug(f"👀 Scanning: {file}")
                if file.is_file():
                    if self._is_ignored(file):
                        self.logger.debug(f"🙈 Ignoring: {file}")
                        continue
                    else:
                        self.logger.debug(f"🚶🏽 Going to read: {file}")
                        yield self._read_file(file)
        else:
            self.logger.error(f"❌ Saving error: {FileNotFoundError(f'Source <<not>> found')}")
            yield FileError(path=str(self.source.absolute()), error=FileNotFoundError(f"Source <<not>> found"))

    def _read_file(self, file: Path) -> FileResult:
        self.logger.info(f"📖 Reading: {file}")
        try:
            content = file.read_text(encoding='utf-8')
            relative_path = file.relative_to(self.base_path)
            return FileDetails(path=str(file), content=content, rel_path=str(relative_path))
        except Exception as e:
            self.logger.error(f"❌ Reading error: {e}")
            return FileError(path=str(file), error=e)

    def save_file(self, result: FileDetails) -> FileResult:
        self.logger.debug(f"📝 Saving: {result.path}")
        try:
            src_path = Path(result.path)

            if self.destination:
                if self.source.is_file():
                    if self.destination.is_dir():
                        target = self.destination / src_path.name
                    else:
                        target = self.destination
                else:
                    relative = src_path.relative_to(self.source)
                    target = self.destination / relative
            else:
                target = src_path  # Overwrite in place

            if target.exists() and not self.overwrite:
                self.logger.warning(f"⚠️ Skipped (exists): {target}")
                return FileResult()

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(result.content, encoding='utf-8')
            return FileResult()
        except Exception as e:
            self.logger.error(f"❌ Saving error: {e}")
            return FileError(path=str("target"), error=e)


def main():
    # Example file paths
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    source = "SampleCode/sample-lib"
    source_path = str(Path(PROJECT_ROOT / source).absolute())

    # Example file paths
    destination = "SampleCode/sample-lib-com"
    destination_path = str(Path(PROJECT_ROOT / destination).absolute())

    processor = AnotherFileProcessor(
        source_str=source_path,
        dest_str=destination_path,
        overwrite=True
    )

    for file in processor.stream_files():
        if isinstance(file, FileDetails):
            print(f"📄 Processing: {file.path}")
            file.content = file.content.upper()
            result = processor.save_file(file)
            if isinstance(result, FileError):
                print(f"Save failed: {result}")
        elif isinstance(file, FileError):
            print(f"Read failed: {file}")


if __name__ == "__main__":
    main()
