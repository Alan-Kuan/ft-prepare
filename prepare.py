from openai.validators import get_validators
import pandas as pd

def apply_remediations(data):
    df = pd.DataFrame(data, dtype=str).fillna('')

    validators = get_validators()
    for validator in validators:
        remediation = validator(df)
        if remediation is not None:
            if remediation.necessary_fn is not None:
                df = remediation.necessary_fn(df)
            if remediation.optional_fn is not None:
                df = remediation.optional_fn(df)

    jsonl = df[['prompt', 'completion']].to_json(
        lines=True, orient='records', force_ascii=False
    )
    return jsonl
