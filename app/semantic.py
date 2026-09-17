import numpy as np
import onnxruntime as ort

from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer


MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_FILE = "onnx/model_quint8_avx2.onnx"
MAX_LENGTH = 256


tokenizer_path = hf_hub_download(
    repo_id=MODEL_ID,
    filename="tokenizer.json",
)

model_path = hf_hub_download(
    repo_id=MODEL_ID,
    filename=MODEL_FILE,
)


tokenizer = Tokenizer.from_file(
    tokenizer_path
)

tokenizer.enable_truncation(
    max_length=MAX_LENGTH
)

tokenizer.enable_padding()


session_options = ort.SessionOptions()

session_options.intra_op_num_threads = 1
session_options.inter_op_num_threads = 1

session = ort.InferenceSession(
    model_path,
    sess_options=session_options,
    providers=["CPUExecutionProvider"],
)


def create_embeddings(texts):
    encoded = tokenizer.encode_batch(
        texts
    )

    input_ids = np.array(
        [
            item.ids
            for item in encoded
        ],
        dtype=np.int64,
    )

    attention_mask = np.array(
        [
            item.attention_mask
            for item in encoded
        ],
        dtype=np.int64,
    )

    token_type_ids = np.array(
        [
            item.type_ids
            for item in encoded
        ],
        dtype=np.int64,
    )

    inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": token_type_ids,
    }

    outputs = session.run(
        None,
        inputs,
    )

    token_embeddings = outputs[0]

    mask = attention_mask[
        :, :, None
    ].astype(
        np.float32
    )

    embeddings = (
        (
            token_embeddings
            * mask
        ).sum(
            axis=1
        )
        / np.clip(
            mask.sum(
                axis=1
            ),
            1e-9,
            None,
        )
    )

    norms = np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True,
    )

    embeddings = (
        embeddings
        / np.clip(
            norms,
            1e-12,
            None,
        )
    )

    return embeddings


def calculate_semantic_similarity(
    resume_text,
    job_text,
):
    if not resume_text or not job_text:
        return 0

    embeddings = create_embeddings(
        [
            resume_text,
            job_text,
        ]
    )

    similarity = float(
        np.dot(
            embeddings[0],
            embeddings[1],
        )
    )

    return round(
        similarity * 100,
        2,
    )