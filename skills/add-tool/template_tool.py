from devpack.tools.base_tool import BaseTool

class {{Name}}Tool(BaseTool):
    name = "{{name}}"

    def download_url(self) -> str:
        if self.install_method == "binary":
            return "https://example.com/{{name}}-{{version}}-{{os}}-{{arch}}.tar.gz"
        return ""

    def install(self, destination: str) -> None:
        pass
