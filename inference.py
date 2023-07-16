import os
import sys
import time
import torch
from autograd_4bit import (
    load_llama_model_4bit_low_ram,
    Autograd4bitQuantLinear,
    load_llama_model_4bit_low_ram_and_offload,
)
from monkeypatch.peft_tuners_lora_monkey_patch import (
    replace_peft_model_with_gptq_lora_model,
)

replace_peft_model_with_gptq_lora_model()

# config_path = './llama-13b-4bit/'
# model_path = './llama-13b-4bit.pt'
# model, tokenizer = load_llama_model_4bit_low_ram(config_path, model_path, groupsize=-1)

# config_path = "/mnt/md0/text-generation-webui/models/Neko-Institute-of-Science_LLaMA-30B-4bit-128g"
# model_path = "/mnt/md0/text-generation-webui/models/Neko-Institute-of-Science_LLaMA-30B-4bit-128g/llama-30b-4bit-128g.safetensors"
# model, tokenizer = load_llama_model_4bit_low_ram(config_path, model_path, groupsize=-1)

# config_path = "/mnt/md0/text-generation-webui/models/TheBloke_WizardLM-30B-GPTQ"
# model_path = "/mnt/md0/text-generation-webui/models/TheBloke_WizardLM-30B-GPTQ/wizardlm-30b-GPTQ-4bit.act.order.safetensors"
# model, tokenizer = load_llama_model_4bit_low_ram(config_path, model_path, groupsize=-1)

config_path = "/mnt/md0/text-generation-webui/models/TheBloke_WizardLM-30B-GPTQ"
model_path = "/mnt/md0/text-generation-webui/models/TheBloke_WizardLM-30B-GPTQ/wizardlm-30b-GPTQ-4bit.act.order.safetensors"
lora_path = "./trained_loras/ald_batchsize128_qlora-8-16_cutoff384_epochs2_wizard30b/checkpoint-164"
model, tokenizer = load_llama_model_4bit_low_ram_and_offload(
    config_path, model_path, lora_path=lora_path, groupsize=-1
)

print("Fitting 4bit scales and zeros to half")
model.half()
for n, m in model.named_modules():
    if isinstance(m, Autograd4bitQuantLinear):
        if m.is_v1_model:
            m.zeros = m.zeros.half()
        m.scales = m.scales.half()
        m.bias = m.bias.half()

print("Apply AMP Wrapper ...")
from amp_wrapper import AMPWrapper

wrapper = AMPWrapper(model)
wrapper.apply_generate()

prompt = """I think the meaning of life is"""
batch = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
batch = {k: v.cuda() for k, v in batch.items()}

start = time.time()
with torch.no_grad():
    generated = model.generate(
        inputs=batch["input_ids"],
        do_sample=True,
        use_cache=True,
        repetition_penalty=1.1,
        max_new_tokens=20,
        temperature=0.9,
        top_p=0.95,
        top_k=40,
        return_dict_in_generate=True,
        output_attentions=False,
        output_hidden_states=False,
        output_scores=False,
    )
result_text = tokenizer.decode(generated["sequences"].cpu().tolist()[0])
end = time.time()
print(result_text)
print(end - start)
