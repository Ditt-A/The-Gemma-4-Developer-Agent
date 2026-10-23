ALLOWED = {'.yaml', '.yml', '.md', '.txt', '.py', '.json', '.safetensors'}
assert set(FILES) == set(EXPECTED_MEMBER_HASHES)
assert 'agent.yaml' in FILES
for name, content in FILES.items():
    relative = PurePosixPath(name)
    assert not relative.is_absolute() and '..' not in relative.parts
    assert relative.suffix.lower() in ALLOWED
    assert hashlib.sha256(content.encode('utf-8')).hexdigest() == EXPECTED_MEMBER_HASHES[name]
    path = AGENT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode('utf-8'))

class Loader(yaml.SafeLoader):
    pass
def include(loader, node):
    name = loader.construct_scalar(node)
    assert name in FILES, name
    return FILES[name] if name.endswith(('.md', '.txt')) else yaml.safe_load(FILES[name])
Loader.add_constructor('!include', include)
agent = yaml.load(FILES['agent.yaml'], Loader=Loader)
generation = agent['generate_content_config']
evaluation = yaml.safe_load(FILES['eval_config.yaml'])['evaluation']
assert agent['model'] in {'gemma-4-31b-it-qat-w4a16-ct', 'gemma-4-12b-it-qat-w4a16-ct', 'gemma-4-e4b-it-qat-w4a16-ct', 'gemma-4-e2b-it-qat-w4a16-ct'}
assert 'submit_patch' in agent['tools']
assert 1 <= generation['max_output_tokens'] <= 32768
assert 0 <= generation.get('thinking_config', {}).get('thinking_budget', 4096) <= 32768
assert all(evaluation[key] > 0 for key in ('timeout_seconds', 'max_tool_calls', 'max_time_minutes', 'max_turns'))
assert len(agent['instruction']) < 1000000
assert sum(len(v.encode('utf-8')) for v in FILES.values()) < 3 * 1024**3
print('Archive contract, model, tools, include paths and budgets passed.')
