import unittest

import requests
from PIL import Image
from src.open_flamingo.factory import create_model_and_transforms


class TestFlamingoModel(unittest.TestCase):
    def test_forward_pass(self):
        model, image_processor, tokenizer = create_model_and_transforms(
            "openai/clip-vit-base-patch32", "facebook/opt-125m")

        image = Image.open(requests.get(
            "http://images.cocodataset.org/val2017/000000039769.jpg", stream=True).raw)
        vis_x = image_processor(images=[image, image], return_tensors="pt")[
            "pixel_values"]
        lang_x = tokenizer(["<image> A dog", "<image> A cat"],
                           return_tensors="pt")["input_ids"]

        # try batched forward pass
        model(vis_x, lang_x)

    def test_generate(self):
        model, image_processor, tokenizer = create_model_and_transforms(
            "openai/clip-vit-base-patch32", "facebook/opt-125m")

        image = Image.open(requests.get(
            "http://images.cocodataset.org/val2017/000000039769.jpg", stream=True).raw)
        vis_x = image_processor(images=[image, image], return_tensors="pt")[
            "pixel_values"]
        lang_x = tokenizer(["<image> A dog", "<image> A cat <|endofchunk|>"], max_length=10,
                           padding=True, truncation=True, return_tensors="pt")

        # try batched generation
        out = model.greedy_generate(vis_x,
                                    lang_x["input_ids"],
                                    attention_mask=lang_x["attention_mask"],
                                    max_length=20,
                                    eoc_token_id=tokenizer.encode(
                                        "<|endofchunk|>")[0],
                                    pad_token_id=tokenizer.pad_token_id)


if __name__ == '__main__':
    unittest.main()