import openai
import threading


class OpenAI:
    def __init__(self, sdk, logger):
        self.logger = logger
        self.ais: dict[str, openai.OpenAI] = {}
        self.aisHistory: dict[str, list[dict[str, str]]] = {}

    def New(self, name, baseUrl, apiKey):
        if name in self.ais:
            self.logger.warning(f"AI {name} already exists, overwriting...")
        self.ais[name] = openai.OpenAI(base_url=baseUrl, api_key=apiKey)
        self.aisHistory[name] = []
        self.logger.info(f"New AI: {name}")

    def Generate(self, name, prompt, **kwargs):
        self.aisHistory[name].append({"role": "user", "content": prompt})
        self.logger.info(f"Generating for {name}: {prompt}")
        tokens = []
        for chunk in self.ais[name].chat.completions.create(
            model=name,
            messages=self.aisHistory[name],
            stream=True,
            **kwargs,
        ):
            token = chunk.choices[0].delta.content
            if token == None:
                token = ""
            yield token
            tokens.append(token)
        answer = "".join(tokens)
        if "<think>" in answer:
            answer = answer.split("</think>")[1]
        self.aisHistory[name].append({"role": "assistant", "content": answer})

    def CleanHistory(self, name):
        self.aisHistory[name] = []
        self.logger.info(f"Cleaned history for {name}")

    def NewTask(self, Generator, CallBack):
        def run():
            try:
                for token in Generator:
                    CallBack(token)
            except Exception as e:
                self.logger.error(f"Error in NewTask: {e}")

        t = threading.Thread(target=run)
        t.start()
        return t
