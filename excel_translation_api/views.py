from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from excel_translation.pipeline import TranslationRunConfig, translate_excel


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _safe_int(value: str | None, default: int | None = None) -> int | None:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


@csrf_exempt
def translate_excel_upload(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    uploaded = request.FILES.get("file") or request.FILES.get("excel") or request.FILES.get("upload")
    if uploaded is None:
        return JsonResponse({"error": "Missing Excel file in form field `file`."}, status=400)

    source_lang = request.POST.get("source", "ja")
    target_lang = request.POST.get("target", "vi")
    formula_mode = request.POST.get("formula_mode", "skip")
    error_policy_mode = request.POST.get("error_policy", "continue-on-error")

    cache_enabled = not _parse_bool(request.POST.get("cache_off"), default=False)
    cache_ttl_seconds = _safe_int(request.POST.get("cache_ttl_seconds"), default=None)

    glossary_file = request.FILES.get("glossary")

    temp_dir = tempfile.mkdtemp(prefix="excel_translate_")
    input_path = None
    output_path = None
    glossary_path = None

    try:
        input_suffix = os.path.splitext(uploaded.name)[1].lower() or ".xlsx"
        input_path = os.path.join(temp_dir, f"input{input_suffix}")
        with open(input_path, "wb") as f:
            for chunk in uploaded.chunks():
                f.write(chunk)

        if glossary_file is not None:
            glossary_suffix = os.path.splitext(glossary_file.name)[1].lower() or ".json"
            glossary_path = os.path.join(temp_dir, f"glossary{glossary_suffix}")
            with open(glossary_path, "wb") as f:
                for chunk in glossary_file.chunks():
                    f.write(chunk)

        output_path = os.path.join(temp_dir, f"output_{target_lang}.xlsx")
        if os.path.exists(output_path):
            os.remove(output_path)

        _run_id = str(uuid.uuid4())
        config = TranslationRunConfig(
            input_path=input_path,
            output_path=output_path,
            source_lang=source_lang,
            target_lang=target_lang,
            glossary_path=glossary_path,
            token_policy_mode="default",
            formula_mode=formula_mode,
            cache_enabled=cache_enabled,
            cache_ttl_seconds=cache_ttl_seconds,
            error_policy_mode=error_policy_mode,
        )

        result = translate_excel(config)
        report = result.get("report")
        output_path_from_result = result.get("output_path") or output_path

        if not output_path_from_result or not os.path.exists(output_path_from_result):
            return JsonResponse({"error": "Translation failed: output file not found."}, status=500)

        with open(output_path_from_result, "rb") as f:
            output_bytes = f.read()

        if report is not None:
            try:
                from excel_translation.reporting import report_to_dict

                report_dict = report_to_dict(report)
                response = HttpResponse(
                    output_bytes,
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                response["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(output_path_from_result)}"'
                )
                response["X-Translation-Report"] = json.dumps(report_dict, ensure_ascii=False)
                return response
            except Exception:
                pass

        response = HttpResponse(
            output_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{os.path.basename(output_path_from_result)}"'
        return response
    except RuntimeError as exc:
        return JsonResponse({"error": str(exc)}, status=501)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
    finally:
        try:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

from __future__ import annotations

import json
import os
import tempfile
import uuid

import shutil

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from excel_translation.pipeline import TranslationRunConfig, translate_excel


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _safe_int(value: str | None, default: int | None = None) -> int | None:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


@csrf_exempt
def translate_excel_upload(request: HttpRequest) -> HttpResponse:
    secret_key = "asdasdasdasdasd";
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    uploaded = request.FILES.get("file") or request.FILES.get("excel") or request.FILES.get("upload")
    if uploaded is None:
        return JsonResponse({"error": "Missing Excel file in form field `file`."}, status=400)

    source_lang = request.POST.get("source", "ja")
    target_lang = request.POST.get("target", "vi")
    formula_mode = request.POST.get("formula_mode", "skip")
    error_policy_mode = request.POST.get("error_policy", "continue-on-error")

    cache_enabled = not _parse_bool(request.POST.get("cache_off"), default=False)
    cache_ttl_seconds = _safe_int(request.POST.get("cache_ttl_seconds"), default=None)

    glossary_file = request.FILES.get("glossary")

    temp_dir = tempfile.mkdtemp(prefix="excel_translate_")
    input_path = None
    output_path = None
    glossary_path = None

    try:
        # Persist uploaded content into a temp file because domain layer expects file paths.
        input_suffix = os.path.splitext(uploaded.name)[1].lower() or ".xlsx"
        input_path = os.path.join(temp_dir, f"input{input_suffix}")
        with open(input_path, "wb") as f:
            for chunk in uploaded.chunks():
                f.write(chunk)

        if glossary_file is not None:
            glossary_suffix = os.path.splitext(glossary_file.name)[1].lower() or ".json"
            glossary_path = os.path.join(temp_dir, f"glossary{glossary_suffix}")
            with open(glossary_path, "wb") as f:
                for chunk in glossary_file.chunks():
                    f.write(chunk)

        # Create output path (ensure it doesn't exist to satisfy overwrite=False default).
        output_path = os.path.join(temp_dir, f"output_{target_lang}.xlsx")
        if os.path.exists(output_path):
            os.remove(output_path)

        run_id = str(uuid.uuid4())
        config = TranslationRunConfig(
            input_path=input_path,
            output_path=output_path,
            source_lang=source_lang,
            target_lang=target_lang,
            glossary_path=glossary_path,
            token_policy_mode="default",
            formula_mode=formula_mode,
            cache_enabled=cache_enabled,
            cache_ttl_seconds=cache_ttl_seconds,
            error_policy_mode=error_policy_mode,
        )

        result = translate_excel(config)
        report = result.get("report")
        output_path_from_result = result.get("output_path") or output_path

        if not output_path_from_result or not os.path.exists(output_path_from_result):
            return JsonResponse({"error": "Translation failed: output file not found."}, status=500)

        with open(output_path_from_result, "rb") as f:
            output_bytes = f.read()

        if report is not None:
            # Keep report lightweight by embedding it in a response header.
            # Consumers can parse JSON from the header.
            try:
                from excel_translation.reporting import report_to_dict

                report_dict = report_to_dict(report)
                response = HttpResponse(
                    output_bytes,
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                response["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(output_path_from_result)}"'
                )
                response["X-Translation-Report"] = json.dumps(report_dict, ensure_ascii=False)
                return response
            except Exception:
                # If report serialization fails, still return the translated file.
                pass

        # Default: return file only.
        response = HttpResponse(
            output_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{os.path.basename(output_path_from_result)}"'
        return response
    except RuntimeError as exc:
        return JsonResponse({"error": str(exc)}, status=501)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
    finally:
        try:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

