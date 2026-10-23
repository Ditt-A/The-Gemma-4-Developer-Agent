import re, time
import litellm
import torch
from adk_submission import VllmConfig, VllmServer, discover_adapters
from adk_submission.discovery import discover_declared_models
from swegemma.config import ALLOWED_ADAPTER_EXTENSIONS

litellm.drop_params = True

ALLOWED_MODEL_NAMES = frozenset({
    'gemma-4-31b-it-qat-w4a16-ct',
    'gemma-4-12b-it-qat-w4a16-ct',
    'gemma-4-e4b-it-qat-w4a16-ct',
    'gemma-4-e2b-it-qat-w4a16-ct',
})
MODEL_VLLM_EXTRA_ARGS = {
    'gemma-4-12b-it-qat-w4a16-ct': (
        '--hf-overrides',
        '{"architectures": ["Gemma4ForCausalLM"], "model_type": "gemma4"}',
    ),
}
_SAFE_PATH_COMPONENT = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*')
INFERENCE_API_KEY = os.environ.get('LOCAL_API_KEY', 'EMPTY')

# Validate single canonical base model and discover any PEFT LoRA adapters in the submission directory.
# Note: sample_submission includes dummy LoRA adapters (adapters/main_lora and adapters/tool_lora)
# shaped for gemma-4-31b-it-qat-w4a16-ct; Cell 2 removes them automatically when MODEL_NAME != 31B.
declared_models = discover_declared_models(AGENT_DIR)
assert len(declared_models) == 1, f'Expected exactly 1 declared model, got: {sorted(declared_models)}'
declared_model = next(iter(declared_models))
assert declared_model in ALLOWED_MODEL_NAMES, f'Unsupported model {declared_model!r}. Allowed: {sorted(ALLOWED_MODEL_NAMES)}'

MODEL_PATH = Path(f'/kaggle/input/models/google/gemma-4/other/{declared_model}/2')
assert MODEL_PATH.exists(), f'Model weights not found at {MODEL_PATH}. Ensure the model input is attached.'

adapters = discover_adapters(str(AGENT_DIR), adapter_extensions=ALLOWED_ADAPTER_EXTENSIONS)
adapter_map = getattr(adapters, 'adapters', None) or {}
for adapter_name in adapter_map:
    assert _SAFE_PATH_COMPONENT.fullmatch(adapter_name), (
        f'Unsafe adapter name {adapter_name!r}: must match [A-Za-z0-9][A-Za-z0-9._-]*'
    )
detected_ranks = [
    r for info in adapter_map.values() if (r := getattr(info, 'rank', None)) is not None and r > 0
]

gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 1
tp_size = 4 if gpu_count >= 4 else (2 if gpu_count >= 2 else 1)

if 'server_instance' in globals() and server_instance is not None:
    server_instance.stop()

vllm_cfg = VllmConfig(
    model=str(MODEL_PATH),
    port=8000,
    host='127.0.0.1',
    tool_call_parser='gemma4',
    reasoning_parser='gemma4',
    max_model_len=32768,
    dtype='bfloat16' if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else 'auto',
    gpu_memory_utilization=0.90,
    enable_auto_tool_choice=True,
    enable_lora=bool(adapter_map),
    max_loras=max(1, len(adapter_map)),
    max_lora_rank=max(detected_ranks) if detected_ranks else 128,
    scheduler_reserve_full_isl=False,
    tensor_parallel_size=tp_size,
    startup_timeout=int(os.environ.get('GEMMA_VLLM_STARTUP_TIMEOUT', '1200')),
    extra_args=MODEL_VLLM_EXTRA_ARGS.get(declared_model, ()),
)
server_instance = VllmServer(vllm_cfg, adapter_manifest=adapters)
server_instance.start()
print(f'vLLM server started on {server_instance.base_url} (tp={tp_size})')

# Register model and LoRA adapter aliases for Google ADK
models = server_instance.create_model_registry(
    aliases=[declared_model],
    model_prefix='openai/',
    api_key=INFERENCE_API_KEY,
)
