import folder_paths
import os
import torch

class LoraSubdirectory:
    def __init__(self):
        pass
    
    @classmethod
    def load_lora_directories(self):
        base_paths = folder_paths.get_folder_paths("loras")
        paths = set()
        for base_path in base_paths:
            if not os.path.isdir(base_path):
                continue
            
            for dirpath, subdirs, filenames in os.walk(base_path, followlinks=True, topdown=True):
                if (any(filename.endswith(".safetensors") for filename in filenames)):
                    paths.add(dirpath)
        output = list(paths)
        output.sort()
        return output

    @classmethod
    def load_lora_files(self, directory):
        output_list = set()
        files, folders_all = folder_paths.recursive_search(directory, excluded_dir_names=[".git"])
        output_list.update(folder_paths.filter_files_extensions(files, folder_paths.supported_pt_extensions))
        files = sorted(list(output_list))
        return files

    @classmethod
    def INPUT_TYPES(s):
        lora_directories = LoraSubdirectory.load_lora_directories()
        types = {
            "required": {
                "model": ("MODEL", {
                    "tooltip": "The diffusion model the LoRA will be applied to."
                }),
                "clip": ("CLIP", {
                    "tooltip": "The CLIP model the LoRA will be applied to."
                }),
                "lora_directory": (lora_directories, {
                    "tooltip": "The subdirectory to populate the dropdown with" 
                })
            }
        }
        # programmatically load all sub-directories into separate inputs
        for index, directory in enumerate(lora_directories):
            types["required"][directory] = (LoraSubdirectory.load_lora_files(directory), {
                "tooltip": "The name of the LoRA from " + directory
            })
        types["required"]["strength_model"] = ("FLOAT", {
            "default": 1.0,
            "min": -100.0,
            "max": 100.0,
            "step": 0.01,
            "tooltip": "How strongly to modify the diffusion model. This value can be negative."
        })
        types["required"]["strength_clip"] = ("FLOAT", {
            "default": 1.0,
            "min": -100.0,
            "max": 100.0,
            "step": 0.01,
            "tooltip": "How strongly to modify the CLIP model. This value can be negative."
        })
        return types

    RETURN_TYPES = ("MODEL", "CLIP",)
    OUTPUT_TOOLTIPS = ("The modified diffusion model.", "The modified CLIP model.",)
    FUNCTION = "load_lora_subdirectory"

    CATEGORY = "loaders"
    DESCRIPTION = "LoRAs are used to modify diffusion and CLIP models, altering the way in which latents are denoised such as applying styles. Multiple LoRA nodes can be linked together."

    def load_lora_subdirectory(self, model, clip, lora_directory, **kwargs):
        if kwargs['strength_model'] == 0 and kwars['strength_clip'] == 0:
            return (model, clip)

        lora_name = kwargs[lora_directory]

        lora_path = folder_paths.get_full_path_or_raise(lora_directory, lora_name)
        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                self.loaded_lora = None

        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            self.loaded_lora = (lora_path, lora)

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, kwargs['strength_model'], kwargs['strength_clip'])
        return (model_lora, clip_lora)

class LoraModelOnlySubdirectory(LoraSubdirectory):
    @classmethod
    def INPUT_TYPES(s):
        lora_directories = LoraSubdirectory.load_lora_directories()
        types = {
            "required": {
                "model": ("MODEL", {
                    "tooltip": "The diffusion model the LoRA will be applied to."
                }),
                "lora_directory": (lora_directories, {
                    "tooltip": "The subdirectory to populate the dropdown with"
                })
            }
        }
        # programmatically load all sub-directories into separate inputs
        for index, directory in enumerate(lora_directories):
            types["required"][directory] = (LoraSubdirectory.load_lora_files(directory), {
                "tooltip": "The name of the LoRA from " + directory
            })
        types["required"]["strength_model"] = ("FLOAT", {
            "default": 1.0,
            "min": -100.0,
            "max": 100.0,
            "step": 0.01,
            "tooltip": "How strongly to modify the diffusion model. This value can be negative."
        })
        return types

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "load_lora_model_only_subdirectory"

    def load_lora_model_only_subdirectory(self, model, lora_directory, **kwargs):
        return (self.load_lora(model, None, lora_directory, **kwargs)[0],)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "LoraSubdirectory": LoraSubdirectory,
    "LoraModelOnlySubdirectory": LoraModelOnlySubdirectory
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraSubdirectory": "Lora Load from Subdirectory",
    "LoraModelOnlySubdirectory": "Lora Load from Subdirectory (Model Only)"
}
