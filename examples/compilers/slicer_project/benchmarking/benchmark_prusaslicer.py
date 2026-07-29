"""Measure PrusaSlicer wall-clock time for manually configured 3MF projects."""

import benchmark_utils as bu


def result_error(result):
    messages = []
    if result.stdout.strip():
        messages.append("stdout:\n{}".format(result.stdout.strip()))
    if result.stderr.strip():
        messages.append("stderr:\n{}".format(result.stderr.strip()))
    return "\n\n".join(messages)[-4000:]


if not bu.PRUSASLICER_EXECUTABLE.is_file():
    raise FileNotFoundError(bu.PRUSASLICER_EXECUTABLE)

bu.ensure_output_dir()

for method_id in bu.METHODS:
    for submeshes in bu.SUBMESH_COUNTS:
        input_path = bu.project_path(method_id, submeshes)
        output_path = bu.gcode_path(method_id, submeshes)
        row = {
            "method_id": method_id,
            "method": bu.METHODS[method_id]["label"],
            "requested_submeshes": submeshes,
            "input_path": str(input_path),
            "gcode_output_path": str(output_path),
            "prusa_slicer_path": str(bu.PRUSASLICER_EXECUTABLE),
            "timestamp": bu.timestamp_utc(),
        }

        try:
            if not input_path.is_file():
                raise FileNotFoundError(input_path)
            if output_path.exists():
                output_path.unlink()

            row.update(bu.inspect_3mf(input_path))
            if row["actual_submeshes"] == "":
                raise RuntimeError(
                    "Could not determine the sub-mesh count in {}".format(input_path)
                )
            result, elapsed_seconds = bu.run_prusaslicer(input_path, output_path)
            row["elapsed_seconds"] = "{:.9f}".format(elapsed_seconds)
            row["return_code"] = result.returncode

            if result.returncode != 0:
                raise RuntimeError(
                    "PrusaSlicer exited with code {}.\n{}".format(
                        result.returncode,
                        result_error(result),
                    )
                )
            if not output_path.is_file():
                raise RuntimeError("PrusaSlicer did not create {}".format(output_path))

            row["status"] = "ok"
            row["error"] = ""
            output_path.unlink()
        except Exception as exc:
            bu.mark_error(row, exc)
            if output_path.exists():
                output_path.unlink()

        bu.write_replace_rows(
            bu.PRUSASLICER_CSV_PATH,
            bu.PRUSASLICER_CSV_FIELDS,
            [row],
        )
        print(
            "{status}: {method} submeshes={submeshes}".format(
                status=row["status"],
                method=bu.METHODS[method_id]["label"],
                submeshes=submeshes,
            )
        )

print("Updated", bu.PRUSASLICER_CSV_PATH)
