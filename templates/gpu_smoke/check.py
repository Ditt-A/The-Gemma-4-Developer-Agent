import requests, time
receipt = {'purpose': '31B vLLM and native tool-call compatibility only',
           'quality_benchmark': False, 'gpu_count': torch.cuda.device_count(),
           'gpu_names': [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]}
try:
    api_url = server_instance.base_url.rstrip('/')
    if not api_url.endswith('/v1'):
        api_url += '/v1'
    headers = {'Authorization': 'Bearer ' + INFERENCE_API_KEY}
    response = requests.get(api_url + '/models', headers=headers, timeout=15)
    response.raise_for_status()
    served = response.json()['data'][0]['id']
    result = requests.post(api_url + '/chat/completions', headers=headers, timeout=60,
        json={'model': served, 'temperature': 0.2, 'top_p': 0.95, 'max_tokens': 1024,
              'messages': [{'role':'system','content':'You inspect source code using the provided native tools. Call read_file to inspect a file; do not invent its contents.'},
                           {'role':'user','content':'Inspect the file pyproject.toml with read_file, start_line 1 and end_line 40. Make that tool call now.'}],
              'tools': [{'type':'function','function':{'name':'read_file','description':'Read a source file.',
                  'parameters':{'type':'object','properties':{'filepath':{'type':'string'},'start_line':{'type':'integer'},'end_line':{'type':'integer'}},'required':['filepath']}}}],
              'tool_choice':'auto', 'chat_template_kwargs':{'enable_thinking':True},
              'thinking_token_budget':256})
    result.raise_for_status()
    payload = result.json()
    message = payload['choices'][0]['message']
    calls = message.get('tool_calls') or []
    assert calls, 'Model emitted no native tool call'
    function = calls[0]['function']
    assert function['name'] == 'read_file', function['name']
    arguments = json.loads(function['arguments'])
    assert arguments.get('filepath') == 'pyproject.toml', arguments
    receipt.update({'native_tool_call_passed':True,'tool_name':function['name'],
                    'tool_arguments':arguments,'usage':payload.get('usage'), 'model':served})
except Exception as exc:
    receipt.update({'native_tool_call_passed':False,'error_type':type(exc).__name__, 'error':str(exc)[:1000]})
    raise
finally:
    receipt['elapsed_seconds'] = round(time.perf_counter() - smoke_started, 2)
    (OUTPUT/'gpu_smoke_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt,indent=2))
    server_instance.stop()
