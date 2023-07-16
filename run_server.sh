#!/bin/bash

export PYTHONPATH=$PYTHONPATH:./

CONFIG_PATH=/mnt/md0/text-generation-webui/models/Neko-Institute-of-Science_LLaMA-30B-4bit-128g
MODEL_PATH=/mnt/md0/text-generation-webui/models/Neko-Institute-of-Science_LLaMA-30B-4bit-128g/llama-30b-4bit-128g.safetensors
LORA_PATH=./trained_loras/ald_batchsize128_qlora-8-16_cutoff384_epochs2_neko30b

# VENV_PATH=
# source $VENV_PATH/bin/activate
# conda activate pvoai
python ./scripts/run_server.py --config_path $CONFIG_PATH --model_path $MODEL_PATH --lora_path $LORA_PATH --groupsize=128 --quant_attn --port 5555 --pub_port 5556