from sed.transpiler.transpiler import make_inputs, make_outputs


def load_tasks_section(tasks_section_config, root):
    tasks = {}
    for key, config in tasks_section_config.items():
        step_type = config.pop("_type")
        if "outputVariables" in config:
            outputs = config.pop("outputVariables")
        else:
            outputs = [f"{key}_result"]

        step_config = {
            "_type": "step",
            "address": f"local:{step_type}",
            "config": {},
            "inputs": make_inputs(step_type, config),
            "_outputs": make_outputs(step_type, outputs),
            "outputs": {output_key: [key, output_key] for output_key in outputs},
        }

        tasks[key] = step_config

    return tasks


