"""Fixed plugin protocol and authority checks. Search/index algorithms are NOT prewritten."""
from .model import RunError
from .store import digest

RECORD_SCHEMA = {"type": "object", "properties": {
    "id": {"type": "string"}, "version": {"type": "integer"},
    "title": {"type": "string"}, "description": {"type": "string"},
    "input_fields": {"type": "array", "items": {"type": "string"}},
    "output_fields": {"type": "array", "items": {"type": "string"}},
    "active": {"type": "boolean"}, "tested": {"type": "boolean"},
    "permissions": {"type": "array", "items": {"type": "string"}}},
    "required": ["id", "version", "title", "description", "input_fields", "output_fields", "active", "tested", "permissions"]}

INPUT_SCHEMA = {"type": "object", "properties": {
    "records": {"type": "array", "items": RECORD_SCHEMA},
    "query": {"type": "string"},
    "required_inputs": {"type": "array", "items": {"type": "string"}}},
    "required": ["records", "query", "required_inputs"]}

ENTRY_SCHEMA = {"type": "object", "properties": {
    "id": {"type": "string"}, "version": {"type": "integer"},
    "terms": {"type": "array", "items": {"type": "string"}},
    "input_fields": {"type": "array", "items": {"type": "string"}}},
    "required": ["id", "version", "terms", "input_fields"]}

OUTPUT_SCHEMA = {"type": "object", "properties": {
    "index": {"type": "array", "items": ENTRY_SCHEMA},
    "matches": {"type": "array", "items": {"type": "string"}}},
    "required": ["index", "matches"]}

PROTOCOL = {
    "kind": "discovery", "input_schema": INPUT_SCHEMA, "output_schema": OUTPUT_SCHEMA,
    "contract": "Given registry records, build an index of exactly the active, tested, compute-only records. "
                "Never include inactive historical versions or failed/overprivileged records. "
                "Derive search terms from each record's id, title, description, input/output fields; "
                "normalize case and accents. Return matching IDs for the query, further restricted to "
                "records containing ALL required_inputs. Empty query returns all compatible IDs. "
                "Nonempty query matches when any normalized whole query token occurs in the entry's terms. "
                "Sort unique terms alphabetically; sort the index and matches by id. "
                "Ignore punctuation; underscores separate words. "
                "Keep each index entry's id, version and input_fields exact. "
                "The host stores the rebuilt index but checks every ID/version against the registry. "
                "This plugin does not control permissions, installation, tests or code execution."
}


def records(store):
    active = {(r["manifest"]["id"], r["version"]) for r in store.registry()}
    result = []
    for version in store.versions():
        m = version["manifest"]
        if m.get("kind", "task") == "discovery":
            continue
        result.append({"id": m["id"], "version": version["version"],
                       "title": m["title"], "description": m["description"],
                       "input_fields": list(m["input_schema"].get("properties", {})),
                       "output_fields": list(m["output_schema"].get("properties", {})),
                       "permissions": m["permissions"],
                       "active": (m["id"], version["version"]) in active,
                       "tested": bool(version["tests"]) and all(x["passed"] for x in version["tests"])})
    return result


def check_result(source, output, required_inputs):
    """Do not trust a generated helper to authorize or silently relabel capabilities."""
    eligible = {r["id"]: r for r in source if r["active"] and r["tested"] and r["permissions"] == ["compute"]}
    index = output.get("index")
    matches = output.get("matches")
    if not isinstance(index, list) or not isinstance(matches, list):
        raise RunError("The catalog did not return an index and result list.")
    try:
        ids = [entry["id"] for entry in index]
        if len(ids) != len(set(ids)) or set(ids) != set(eligible):
            raise RunError("The catalog omitted a valid skill or returned an invalid version.")
        for entry in index:
            original = eligible[entry["id"]]
            if entry["version"] != original["version"] or entry["input_fields"] != original["input_fields"]:
                raise RunError("The catalog must not change a skill version or interface.")
        if len(matches) != len(set(matches)) or any(ident not in eligible for ident in matches):
            raise RunError("The catalog returned an inactive or unknown skill.")
        if any(not set(required_inputs).issubset(eligible[ident]["input_fields"]) for ident in matches):
            raise RunError("The catalog returned an incompatible input schema.")
    except (TypeError, KeyError):
        raise RunError("The catalog returned invalid metadata.") from None
    return output


def invariant_cases():
    """Handwritten platform contract fixtures, distinct from generated domain tests."""
    def record(ident, **updates):
        return {"id": ident, "version": 1, "title": ident, "description": "",
                "input_fields": ["rows"], "output_fields": ["rows"],
                "active": True, "tested": True, "permissions": ["compute"], **updates}
    a = record("clean_rows")
    b = record("render_report", input_fields=["summary"])
    index = [{"id": "clean_rows", "version": 1, "input_fields": ["rows"], "terms": ["clean", "rows"]},
             {"id": "render_report", "version": 1, "input_fields": ["summary"], "terms": ["render", "report", "rows", "summary"]}]
    return [
        {"name": "Inactive and failed records stay outside the index",
         "input": {"records": [a, b, record("old", active=False), record("bad", tested=False),
                                record("unsafe", permissions=["compute", "network"])],
                   "query": "", "required_inputs": []},
         "expected": {"matches": ["clean_rows", "render_report"], "index": index}},
        {"name": "Required input fields restrict selection",
         "input": {"records": [a, b], "query": "", "required_inputs": ["rows"]},
         "expected": {"matches": ["clean_rows"], "index": index}},
        {"name": "Deactivated version is excluded after a correction",
         "input": {"records": [record("clean_rows", active=False), record("clean_rows", version=2)],
                   "query": "clean", "required_inputs": []},
         "expected": {"matches": ["clean_rows"],
                      "index": [{"id": "clean_rows", "version": 2, "input_fields": ["rows"], "terms": ["clean", "rows"]}]}}
    ]


def case_errors(cases):
    """Validate test-author expectations BEFORE implementation using the fixed contract.

    This oracle is for test admission only. It is never a runtime discovery
    fallback, never installs a helper, and does not use candidate code or output.
    The model still supplies the cases; inconsistent expectations are rejected.
    """
    import re
    import unicodedata

    def words(value):
        value = unicodedata.normalize("NFKD", value.lower())
        value = "".join(char for char in value if not unicodedata.combining(char))
        return set(re.findall(r"[^\W_]+", value))

    errors = []
    if not isinstance(cases, list):
        return [{"error": "Test cases must be a list."}]
    for number, case in enumerate(cases):
        try:
            data = case["input"]
            expected = case["expected"]
            index = []
            for record in data["records"]:
                if not (record["active"] and record["tested"] and record["permissions"] == ["compute"]):
                    continue
                sources = [record["id"], record["title"], record["description"], *record["input_fields"], *record["output_fields"]]
                terms = set()
                for source in sources:
                    terms.update(words(source))
                index.append({"id": record["id"], "version": record["version"], "input_fields": record["input_fields"], "terms": sorted(terms)})
            index.sort(key=lambda entry: entry["id"])
            query = words(data["query"])
            required = set(data["required_inputs"])
            matches = [entry["id"] for entry in index
                       if required.issubset(entry["input_fields"]) and (not query or query.intersection(entry["terms"]))]
            contract_expected = {"index": index, "matches": matches}
            if expected != contract_expected:
                differences = []
                supplied_entries = {entry["id"]: entry for entry in expected.get("index", [])}
                for entry in index:
                    supplied = supplied_entries.get(entry["id"], {})
                    supplied_terms = set(supplied.get("terms", []))
                    missing = sorted(set(entry["terms"]) - supplied_terms)
                    extra = sorted(supplied_terms - set(entry["terms"]))
                    if missing or extra:
                        differences.append({"id": entry["id"], "missing_terms": missing, "extra_terms": extra})
                errors.append({"case": number, "name": case.get("name", "Unnamed case"),
                               "error": "Expected output does not match the fixed catalog contract.",
                               "term_differences": differences, "expected_by_contract": contract_expected,
                               "provided_expected": expected})
        except (KeyError, TypeError, AttributeError, ValueError):
            errors.append({"case": number, "error": "Malformed catalog contract test."})
    return errors
