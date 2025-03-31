from collections import defaultdict, deque
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sys

executor = ThreadPoolExecutor()


def topological_sort(elements, dependencies, error):
    graph = defaultdict(list)
    in_degree = {element: 0 for element in elements}
    for element, deps in dependencies.items():
        for dep in deps:
            graph[dep].append(element)
            in_degree[element] += 1
    queue = deque([element for element in elements if in_degree[element] == 0])
    sorted_list = []
    while queue:
        node = queue.popleft()
        sorted_list.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    if len(sorted_list) != len(elements):
        raise error(f"Cycle detected in the dependencies: {elements} -> {dependencies}")
    return sorted_list


def ExecAsync(async_func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, lambda: asyncio.run(async_func(*args, **kwargs)))


class CmdArg:
    def __init__(self):
        self.cmdArgs: list[str] = sys.argv[1:]
        self.bindArgs: list[str] = []
        self.bindArgObjs: dict[str, object] = {}

    def Bind(self, argName: str, argObj: object):
        self.bindArgs.append(argName)
        self.bindArgObjs[argName] = argObj

    def Execute(self):
        for i in range(len(self.cmdArgs)):
            arg = self.cmdArgs[i]
            if arg not in self.bindArgs:
                continue
            if (
                self.cmdArgs[i] == self.cmdArgs[-1]
                or self.cmdArgs[i + 1] in self.bindArgs
            ):
                value = ""
            else:
                value = self.cmdArgs[i + 1]
            self.bindArgObjs[arg](value)
