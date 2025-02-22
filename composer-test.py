from py.nodes.composer import Composer
from py.utils.config import load_nodes_config

config = load_nodes_config()


def main(seed, prompt):

    composer = Composer()
    prompt_final = composer.build_prompt(seed=seed, prompt=prompt)
    print(prompt_final)


if __name__ == "__main__":
    seed = 0
    prompt = "foo, bar, {makeup-color}, {makeup}, {eyewear-shape}"
    main(seed, prompt)
