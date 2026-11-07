# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

import json
import pathlib
import re
import sys

LINE_RE = re.compile(r'<p class="([^"]+)"><span class="n"><a id="t(\d+)"')


def generate_from_html_report(report_dir: pathlib.Path, out_path: pathlib.Path) -> bool:
    status_file = report_dir / "status.json"
    if not status_file.exists():
        return False

    data = json.loads(status_file.read_text(encoding="utf-8"))
    files = data.get("files", {})

    lines_out = ['<coverage version="1">']
    for file_info in files.values():
        index = file_info.get("index", {})
        src_path = index.get("file", "").replace("\\", "/")
        html_name = index.get("url", "")
        if not src_path or not html_name:
            continue

        # Only include files that currently exist in the repo so SonarCloud doesn't complain
        if not pathlib.Path(src_path).exists():
            continue

        html_file = report_dir / html_name
        if not html_file.exists():
            continue

        html_text = html_file.read_text(encoding="utf-8")
        covered_lines = []
        for match in LINE_RE.finditer(html_text):
            classes = match.group(1).split()
            line_num = int(match.group(2))
            if "run" in classes:
                covered_lines.append((line_num, True))
            elif "mis" in classes:
                covered_lines.append((line_num, False))

        if covered_lines:
            lines_out.append(f'  <file path="{src_path}">')
            for line_num, is_covered in covered_lines:
                cov_str = "true" if is_covered else "false"
                lines_out.append(
                    f'    <lineToCover lineNumber="{line_num}" covered="{cov_str}"/>'
                )
            lines_out.append("  </file>")

    lines_out.append("</coverage>")
    out_path.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    return True


def main() -> None:
    out_path = pathlib.Path("sonar-coverage.xml")
    html_dir = pathlib.Path("courseProjectDocs/Setup/coverage-report")
    if generate_from_html_report(html_dir, out_path):
        print(f"Generated Sonar generic coverage report at {out_path}")
    else:
        print("Could not find baseline coverage report", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
