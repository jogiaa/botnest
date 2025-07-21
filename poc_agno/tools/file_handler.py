import traceback
from pathlib import Path
from typing import List, Optional, Union
from dataclasses import dataclass


# --- Sealed Class-like Result Types ---
class FileResult:
    pass


@dataclass
class FileDetails(FileResult):
    size: int
    path: str
    content: str


@dataclass
class FileError(FileResult):
    error: Exception


# --- File Processor Class ---
class OneFileProcessor:
    def __init__(self, source_str: str, dest_str: Optional[str] = None):
        self.source = Path(source_str).resolve()
        self.destination = Path(dest_str).resolve() if dest_str else None

    def read_file(self):
        self.read_file(self.source)

    def read_file(self, file_path: Path) -> Union[FileDetails, FileError]:
        try:
            content = file_path.read_text(encoding='utf-8')
            return FileDetails(
                size=file_path.stat().st_size,
                path=str(file_path),
                content=content
            )
        except Exception as e:
            return FileError(error=e)

    def write_file(self, dest_path: Path, content: str) -> Union[FileResult, FileError]:
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(content, encoding='utf-8')
            return FileResult()  # Acts like Kotlin's `object`
        except Exception as e:
            return FileError(error=e)

    def process(self) -> List[FileResult]:
        results: List[FileResult] = []

        if self.source.is_file():
            result = self.read_file(self.source)
            results.append(result)

            if isinstance(result, FileDetails):
                target = self.destination if self.destination else self.source
                write_result = self.write_file(target, result.content)
                results.append(write_result)

        elif self.source.is_dir():
            for file in self.source.rglob("*"):
                if file.is_file():
                    result = self.read_file(file)
                    results.append(result)

                    if isinstance(result, FileDetails):
                        if self.destination:
                            relative = file.relative_to(self.source)
                            target_path = self.destination / relative
                        else:
                            target_path = file  # overwrite original

                        write_result = self.write_file(target_path, result.content)
                        results.append(write_result)
        else:
            results.append(FileError(error=FileNotFoundError(f"Source path '{self.source}' does not exist")))

        return results


# --- Command-line Interface ---
if __name__ == "__main__":
    source = "koin/examples/coffee-maker"
    destination = "koin/examples/coffee-maker-two"
    processor = OneFileProcessor(source, destination)
    results = processor.process()

    for result in results:
        if isinstance(result, FileDetails):
            print(f"✅ Processed: {result.path} ({result.size} bytes)")
        elif isinstance(result, FileError):
            print("❌ Error:", traceback.format_exception_only(type(result.error), result.error)[0].strip())
