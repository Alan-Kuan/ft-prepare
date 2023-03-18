#!/usr/bin/env bash

# Use this script to directly convert all Q&A pairs inside the given project
# into a jsonl file for fine-tuning.

api_key=''
endpoint=''
project=''

[ -z "$api_key" ] && echo 'api key was not specified' && exit 1
[ -z "$endpoint" ] && echo 'api endpoint was not specified' && exit 1
[ -z "$project" ] && echo 'project name was not specified' && exit 1

output=output.jsonl

curl -X GET "${endpoint}/language/query-knowledgebases/projects/${project}/qnas?api-version=2021-10-01" \
    -H "Ocp-Apim-Subscription-Key: ${api_key}" \
    -H 'Content-Type: application/json' | \
    jq -c 'range(.value | length) as $i | { prompt: .value[$i].questions[], completion: .value[$i].answer }' > $output

# openai tools will append the original filename with '_prepared'
final_output="${output%%.*}_prepared.jsonl"

# remove $final_output if it already exists
[ -f "$final_output" ] && rm $final_output

openai tools fine_tunes.prepare_data -f $output

# add BOM if not exists
# NOTE: MS Learn said that it's required; however, I tried OpenAI's tool and it didn't require that
# sed -i '1s/^\(\xef\xbb\xbf\)\?/\xef\xbb\xbf/' $final_output
