from pydantic_settings import BaseSettings


class Deployment(BaseSettings):
    project: str
    stage: str
    pipeline: str

    @property
    def stack_name(self):
        name = f'{self.project}-{self.pipeline.replace("_", "-")}-{self.stage}'
        # A stack name can contain only alphanumeric characters (case-sensitive) and hyphens.
        # It must start with an alphabetic character and can't be longer than 128 characters.
        assert (
            len(name) <= 128
        ), f"Stack name {name} is too long, must be less than 128 characters"
        for char in name:
            assert (
                char.isalnum() or char == "-"
            ), f"Stack name {name} contains invalid character {char}"
        return name
