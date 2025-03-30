from collections import defaultdict, deque
import threading
from typing import Callable, Any, Union


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


class Promise:
    def __init__(self, executor: Callable):
        self._state = "pending"
        self._value: Any = None
        self._reason: Any = None
        self._then_callbacks = []
        self._catch_callbacks = []

        def resolve(value: Any) -> None:
            if self._state == "pending":
                self._state = "fulfilled"
                self._value = value
                self._execute_callbacks(self._then_callbacks, value)

        def reject(reason: Any) -> None:
            if self._state == "pending":
                self._state = "rejected"
                self._reason = reason
                self._execute_callbacks(self._catch_callbacks, reason)

        try:
            threading.Thread(
                target=executor, args=(resolve, reject), daemon=True
            ).start()
        except Exception as e:
            reject(e)

    def _execute_callbacks(self, callbacks: list, arg: Any) -> None:
        for callback in callbacks:
            try:
                threading.Thread(target=callback, args=(arg,), daemon=True).start()
            except Exception as e:
                print(f"Error executing callback: {e}")

    def then(self, on_fulfilled: Union[Callable, None]) -> "Promise":
        if self._state == "fulfilled":
            threading.Thread(
                target=on_fulfilled, args=(self._value,), daemon=True
            ).start()
        elif self._state == "pending":
            self._then_callbacks.append(on_fulfilled)
        return self

    def catch(self, on_rejected: Union[Callable, None]) -> "Promise":
        if self._state == "rejected":
            threading.Thread(
                target=on_rejected, args=(self._reason,), daemon=True
            ).start()
        elif self._state == "pending":
            self._catch_callbacks.append(on_rejected)
        return self
